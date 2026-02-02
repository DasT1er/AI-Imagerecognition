"""
Aim engine: target selection, smooth aiming, prediction, humanization.
Supports direct head-class targeting (aims at head bbox center when detected).
"""
import math
import time
import random
from typing import List, Optional, Tuple
from dataclasses import dataclass

from core.detector import Detection
from utils.math_utils import (
    distance, calculate_move_delta, add_jitter,
    predict_position, clamp,
)


@dataclass
class TrackedTarget:
    """Target with velocity tracking for prediction."""
    detection: Detection
    aim_point: Tuple[float, float]       # In capture-region coords
    screen_point: Tuple[float, float]    # In full screen coords
    distance_to_crosshair: float
    is_head: bool = False                # True if this is a head-class detection
    velocity: Tuple[float, float] = (0.0, 0.0)
    last_seen: float = 0.0


class AimEngine:
    """Handles target selection, aim calculation, and smooth movement."""

    def __init__(self, config):
        self.config = config
        self._prev_targets: dict = {}
        self._current_target: Optional[TrackedTarget] = None
        self._velocity_history: dict = {}  # EMA velocity per target key
        self._smoothed_aim: Optional[Tuple[float, float]] = None  # EMA-smoothed aim point
        self._lock_timer: float = 0.0  # When we locked onto current target
        self._target_lost_frames: int = 0  # Frames since locked target was last seen

    def select_target(self, detections: List[Detection],
                      screen_center: Tuple[int, int],
                      capture_offset: Tuple[int, int]) -> Optional[TrackedTarget]:
        """
        Select best target from detections.
        Uses target locking to prevent flickering between enemies.
        If prefer_head is on and a head-class is detected, aim at head bbox center.
        Otherwise fall back to body bbox + bone ratio.
        """
        if not detections:
            self._target_lost_frames += 1
            # Keep target for a few frames to avoid losing it on detection flicker
            if self._current_target is not None and self._target_lost_frames < 5:
                return self._current_target
            self._current_target = None
            self._smoothed_aim = None
            return None

        cfg = self.config
        fov = cfg["fov_radius"]
        now = time.perf_counter()
        head_ids = set(cfg.get("head_class_ids", [1, 3]))
        prefer_head = cfg.get("prefer_head", True)

        candidates = []

        for det in detections:
            is_head = det.class_id in head_ids

            if is_head:
                aim_local = det.center  # Center of head bbox = direct headshot
            else:
                aim_local = det.get_aim_point(
                    bone=cfg["target_bone"],
                    head_r=cfg["head_ratio"],
                    neck_r=cfg["neck_ratio"],
                    chest_r=cfg["chest_ratio"],
                    body_r=cfg["body_ratio"],
                )

            aim_screen = (
                aim_local[0] + capture_offset[0],
                aim_local[1] + capture_offset[1],
            )
            dist = distance(screen_center, aim_screen)
            if dist > fov:
                continue

            velocity = self._track_velocity(det, aim_screen, now)

            candidates.append(TrackedTarget(
                detection=det,
                aim_point=aim_local,
                screen_point=aim_screen,
                distance_to_crosshair=dist,
                is_head=is_head,
                velocity=velocity,
                last_seen=now,
            ))

        if not candidates:
            self._target_lost_frames += 1
            if self._current_target is not None and self._target_lost_frames < 5:
                return self._current_target
            self._current_target = None
            self._smoothed_aim = None
            return None

        # --- Target locking: stick to current target unless it's gone ---
        if self._current_target is not None:
            # Find the candidate closest to our locked target
            best_match = None
            best_match_dist = float('inf')
            for c in candidates:
                d = distance(self._current_target.screen_point, c.screen_point)
                if d < best_match_dist:
                    best_match = c
                    best_match_dist = d

            # If locked target is still nearby (within 80px), keep it
            # Only switch if a MUCH better target exists (head vs body, or way closer)
            if best_match is not None and best_match_dist < 80:
                self._target_lost_frames = 0
                # Smooth the aim point (EMA) to prevent bbox jitter
                best_match = self._smooth_aim_point(best_match, screen_center)
                self._current_target = best_match
                return best_match

            # Locked target gone - check if we should switch or wait
            lock_duration = now - self._lock_timer
            if lock_duration < 0.15:
                # Very recently locked, don't switch yet (anti-flicker)
                self._target_lost_frames += 1
                if self._target_lost_frames < 5:
                    return self._current_target

        # --- No lock or lock broken: pick best new target ---
        if prefer_head:
            head_candidates = [c for c in candidates if c.is_head]
            body_candidates = [c for c in candidates if not c.is_head]
            head_candidates.sort(key=lambda t: t.distance_to_crosshair)
            body_candidates.sort(key=lambda t: t.distance_to_crosshair)
            sorted_candidates = head_candidates + body_candidates
        else:
            sorted_candidates = self._sort_candidates(candidates, cfg["target_sort"])

        new_target = sorted_candidates[0]
        self._smoothed_aim = None  # Reset smoothing for new target
        new_target = self._smooth_aim_point(new_target, screen_center)
        self._current_target = new_target
        self._lock_timer = now
        self._target_lost_frames = 0
        return new_target

    def _smooth_aim_point(self, target: TrackedTarget,
                          screen_center: Tuple[int, int] = None) -> TrackedTarget:
        """Apply EMA smoothing to the aim point to reduce bbox jitter."""
        alpha = 0.3  # Low alpha = less lag, more responsive but still smoothed
        sp = target.screen_point

        if self._smoothed_aim is None:
            self._smoothed_aim = sp
        else:
            # EMA: new = alpha * old + (1-alpha) * raw
            sx = alpha * self._smoothed_aim[0] + (1 - alpha) * sp[0]
            sy = alpha * self._smoothed_aim[1] + (1 - alpha) * sp[1]
            self._smoothed_aim = (sx, sy)

        # Calculate correct distance_to_crosshair from screen center
        if screen_center is not None:
            dist = distance(screen_center, self._smoothed_aim)
        else:
            dist = target.distance_to_crosshair

        return TrackedTarget(
            detection=target.detection,
            aim_point=target.aim_point,
            screen_point=self._smoothed_aim,
            distance_to_crosshair=dist,
            is_head=target.is_head,
            velocity=target.velocity,
            last_seen=target.last_seen,
        )

    def _track_velocity(self, det: Detection, aim_screen: tuple,
                        now: float) -> Tuple[float, float]:
        """Track velocity with exponential moving average for smoother prediction."""
        # Use wider grid cells (//30) to improve tracking consistency
        target_key = f"{det.class_id}_{int(det.center[0]//30)}_{int(det.center[1]//30)}"
        velocity = (0.0, 0.0)

        if target_key in self._prev_targets:
            prev = self._prev_targets[target_key]
            dt = now - prev.last_seen
            if 0 < dt < 0.3:
                raw_vx = (aim_screen[0] - prev.screen_point[0]) / dt
                raw_vy = (aim_screen[1] - prev.screen_point[1]) / dt

                # EMA smoothing for velocity
                alpha = 0.3
                prev_vel = self._velocity_history.get(target_key, (0.0, 0.0))
                vx = alpha * raw_vx + (1 - alpha) * prev_vel[0]
                vy = alpha * raw_vy + (1 - alpha) * prev_vel[1]
                velocity = (vx, vy)
                self._velocity_history[target_key] = velocity

        # Update prev tracking
        self._prev_targets[target_key] = TrackedTarget(
            detection=det, aim_point=(0, 0), screen_point=aim_screen,
            distance_to_crosshair=0, velocity=velocity, last_seen=now,
        )

        # Cleanup old entries (older than 1 second)
        stale = [k for k, v in self._prev_targets.items() if now - v.last_seen > 1.0]
        for k in stale:
            del self._prev_targets[k]
            self._velocity_history.pop(k, None)

        return velocity

    def _sort_candidates(self, candidates: list, sort_mode: str) -> list:
        if sort_mode == "distance":
            candidates.sort(key=lambda t: t.distance_to_crosshair)
        elif sort_mode == "confidence":
            candidates.sort(key=lambda t: -t.detection.confidence)
        elif sort_mode == "area":
            candidates.sort(key=lambda t: -t.detection.area)
        return candidates

    def compute_move(self, target: TrackedTarget,
                     screen_center: Tuple[int, int]) -> Tuple[int, int]:
        """
        Compute mouse move delta (dx, dy) to move towards target.
        Improved: distance-based acceleration, better flick, less jitter near target.
        """
        cfg = self.config
        aim_point = target.screen_point

        # Prediction
        if cfg["prediction_enabled"] and (
            abs(target.velocity[0]) > 10 or abs(target.velocity[1]) > 10
        ):
            aim_point = predict_position(
                aim_point, target.velocity, cfg["prediction_factor"]
            )

        dist = distance(screen_center, aim_point)

        # Minimum movement threshold - avoid micro-twitching near target
        if dist < cfg.get("min_move_threshold", 1.0):
            return (0, 0)

        # Flick: very close target -> snap directly
        if cfg["flick_enabled"] and dist < cfg["flick_threshold"]:
            dx = aim_point[0] - screen_center[0]
            dy = aim_point[1] - screen_center[1]
            if cfg["humanize"]:
                # Reduced jitter for flicks
                dx, dy = add_jitter(dx, dy, cfg["humanize_jitter"] * 0.3)
            return (int(round(dx)), int(round(dy)))

        # Distance-based smoothing: move faster when far, slower when close
        smoothing = cfg["smoothing"]
        if cfg.get("distance_scaling", True):
            # Near target: more smoothing (precise), far: less smoothing (fast)
            norm_dist = clamp(dist / cfg["fov_radius"], 0.0, 1.0)
            # Lerp: close = smoothing * 1.3, far = smoothing * 0.5
            smoothing = smoothing * (1.3 - 0.8 * norm_dist)
            smoothing = clamp(smoothing, 0.05, 0.95)

        # Calculate move delta
        dx, dy = calculate_move_delta(
            current=screen_center,
            target=aim_point,
            smoothing=smoothing,
            curve=cfg["smoothing_curve"],
            max_move=cfg["max_move_per_tick"],
        )

        # Humanize - scale jitter based on distance (less jitter when close)
        if cfg["humanize"]:
            jitter_scale = clamp(dist / 100, 0.1, 1.0)
            dx, dy = add_jitter(dx, dy, cfg["humanize_jitter"] * jitter_scale)

            # Random micro-delay
            delay_min = cfg["humanize_delay_min"] / 1000
            delay_max = cfg["humanize_delay_max"] / 1000
            if delay_max > delay_min:
                time.sleep(random.uniform(delay_min, delay_max))

        return (int(round(dx)), int(round(dy)))

    def is_on_target(self, target: TrackedTarget,
                     screen_center: Tuple[int, int],
                     threshold: float = 5.0) -> bool:
        return distance(screen_center, target.screen_point) < threshold

    def reset(self):
        self._current_target = None
        self._smoothed_aim = None
        self._target_lost_frames = 0
        self._prev_targets.clear()
        self._velocity_history.clear()
