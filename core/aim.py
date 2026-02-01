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

    def select_target(self, detections: List[Detection],
                      screen_center: Tuple[int, int],
                      capture_offset: Tuple[int, int]) -> Optional[TrackedTarget]:
        """
        Select best target from detections.
        If prefer_head is on and a head-class is detected, aim at head bbox center.
        Otherwise fall back to body bbox + bone ratio.
        """
        if not detections:
            self._current_target = None
            return None

        cfg = self.config
        fov = cfg["fov_radius"]
        now = time.perf_counter()
        head_ids = set(cfg.get("head_class_ids", [1, 3]))
        prefer_head = cfg.get("prefer_head", True)

        # Group detections: find heads and bodies
        heads = [d for d in detections if d.class_id in head_ids]
        bodies = [d for d in detections if d.class_id not in head_ids]

        candidates = []

        # Process head detections (aim at center of head bbox)
        if prefer_head:
            for det in heads:
                aim_local = det.center  # Center of head bbox = direct headshot
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
                    is_head=True,
                    velocity=velocity,
                    last_seen=now,
                ))

        # Process body detections (use bone ratio)
        for det in bodies:
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
                is_head=False,
                velocity=velocity,
                last_seen=now,
            ))

        if not candidates:
            self._current_target = None
            return None

        # Prioritize: head targets first (closer is better), then body targets
        if prefer_head:
            head_candidates = [c for c in candidates if c.is_head]
            body_candidates = [c for c in candidates if not c.is_head]
            head_candidates.sort(key=lambda t: t.distance_to_crosshair)
            body_candidates.sort(key=lambda t: t.distance_to_crosshair)
            sorted_candidates = head_candidates + body_candidates
        else:
            sorted_candidates = self._sort_candidates(candidates, cfg["target_sort"])

        # Sticky targeting: prefer current target if still visible
        if self._current_target is not None:
            for c in sorted_candidates:
                prev = self._current_target.screen_point
                if distance(prev, c.screen_point) < 40:
                    self._current_target = c
                    return c

        self._current_target = sorted_candidates[0]
        return sorted_candidates[0]

    def _track_velocity(self, det: Detection, aim_screen: tuple,
                        now: float) -> Tuple[float, float]:
        """Track velocity with exponential moving average for smoother prediction."""
        target_key = f"{det.class_id}_{int(det.center[0]//15)}_{int(det.center[1]//15)}"
        velocity = (0.0, 0.0)

        if target_key in self._prev_targets:
            prev = self._prev_targets[target_key]
            dt = now - prev.last_seen
            if 0 < dt < 0.3:
                raw_vx = (aim_screen[0] - prev.screen_point[0]) / dt
                raw_vy = (aim_screen[1] - prev.screen_point[1]) / dt

                # EMA smoothing for velocity
                alpha = 0.4
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

        # Minimum movement threshold - avoid micro-twitching
        if dist < cfg.get("min_move_threshold", 0.5):
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
        self._prev_targets.clear()
        self._velocity_history.clear()
