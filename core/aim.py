"""
Aim engine: target selection and mouse movement.
Direct aiming with target lock - no smoothing layers.
"""
import math
import time
import random
from typing import List, Optional, Tuple
from dataclasses import dataclass

from core.detector import Detection
from utils.math_utils import distance, clamp, add_jitter


@dataclass
class TrackedTarget:
    """Target with tracking info."""
    detection: Detection
    aim_point: Tuple[float, float]       # In capture-region coords
    screen_point: Tuple[float, float]    # In full screen coords
    distance_to_crosshair: float
    is_head: bool = False
    last_seen: float = 0.0


class AimEngine:
    """Target selection and direct mouse movement."""

    def __init__(self, config):
        self.config = config
        self._current_target: Optional[TrackedTarget] = None
        self._lock_timer: float = 0.0
        self._lost_frames: int = 0
        self._locked_det_center: Optional[Tuple[float, float]] = None

    def select_target(self, detections: List[Detection],
                      screen_center: Tuple[int, int],
                      capture_offset: Tuple[int, int]) -> Optional[TrackedTarget]:
        """
        Select best target. Hard-locks onto a target until it dies/leaves FOV.
        Prefers head-class detections when available.
        """
        cfg = self.config
        fov = cfg["fov_radius"]
        now = time.perf_counter()
        head_ids = set(cfg.get("head_class_ids", [1, 3]))
        prefer_head = cfg.get("prefer_head", True)

        # Build candidate list
        candidates = []
        for det in detections:
            is_head = det.class_id in head_ids

            if is_head:
                aim_local = det.center
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

            candidates.append(TrackedTarget(
                detection=det,
                aim_point=aim_local,
                screen_point=aim_screen,
                distance_to_crosshair=dist,
                is_head=is_head,
                last_seen=now,
            ))

        # No candidates found
        if not candidates:
            self._lost_frames += 1
            if self._current_target is not None and self._lost_frames < 5:
                return self._current_target
            self._current_target = None
            self._locked_det_center = None
            return None

        # --- Hard target lock using bbox center in LOCAL coords ---
        # This prevents snapping: we track the detection's position in the
        # capture frame, not screen coords (which shift as aim moves).
        if self._current_target is not None and self._locked_det_center is not None:
            best_match = None
            best_dist = float('inf')

            for c in candidates:
                # Match by detection bbox center in capture-local coordinates
                d = distance(self._locked_det_center, c.detection.center)
                if d < best_dist:
                    best_match = c
                    best_dist = d

            # Locked target still present (within 120px in local coords)
            if best_match is not None and best_dist < 120:
                self._lost_frames = 0
                self._locked_det_center = best_match.detection.center
                self._current_target = best_match
                return best_match

            # Target gone but lock is fresh -> hold a few frames
            if now - self._lock_timer < 0.2 and self._lost_frames < 5:
                self._lost_frames += 1
                return self._current_target

        # --- Pick new target ---
        if prefer_head:
            heads = [c for c in candidates if c.is_head]
            bodies = [c for c in candidates if not c.is_head]
            heads.sort(key=lambda t: t.distance_to_crosshair)
            bodies.sort(key=lambda t: t.distance_to_crosshair)
            sorted_cands = heads + bodies
        else:
            sorted_cands = sorted(candidates, key=lambda t: t.distance_to_crosshair)

        chosen = sorted_cands[0]
        self._current_target = chosen
        self._locked_det_center = chosen.detection.center
        self._lock_timer = now
        self._lost_frames = 0
        return chosen

    def compute_move(self, target: TrackedTarget,
                     screen_center: Tuple[int, int]) -> Tuple[int, int]:
        """
        Compute mouse delta to move toward target.
        Simple proportional move - no smoothing curves, no bezier, no EMA.
        Just move a fraction of the distance each frame.
        """
        cfg = self.config
        tx, ty = target.screen_point
        cx, cy = screen_center

        dx = tx - cx
        dy = ty - cy
        dist = math.hypot(dx, dy)

        # Dead zone - already on target
        if dist < cfg.get("min_move_threshold", 1.5):
            return (0, 0)

        # Simple speed factor: move this fraction of the remaining distance
        # smoothing=0 -> speed=1.0 (instant), smoothing=0.9 -> speed=0.1
        speed = 1.0 - clamp(cfg["smoothing"], 0.0, 0.95)

        move_x = dx * speed
        move_y = dy * speed

        # Cap maximum move per tick
        move_dist = math.hypot(move_x, move_y)
        max_move = cfg["max_move_per_tick"]
        if move_dist > max_move:
            scale = max_move / move_dist
            move_x *= scale
            move_y *= scale

        # Never overshoot: don't move more than actual distance
        if abs(move_x) > abs(dx):
            move_x = dx
        if abs(move_y) > abs(dy):
            move_y = dy

        # Small jitter for humanization (optional, very subtle)
        if cfg["humanize"] and dist > 5:
            jitter = cfg["humanize_jitter"] * clamp(dist / 150, 0.05, 0.5)
            move_x += random.gauss(0, jitter)
            move_y += random.gauss(0, jitter)

        return (int(round(move_x)), int(round(move_y)))

    def is_on_target(self, target: TrackedTarget,
                     screen_center: Tuple[int, int],
                     threshold: float = 5.0) -> bool:
        return distance(screen_center, target.screen_point) < threshold

    def reset(self):
        self._current_target = None
        self._locked_det_center = None
        self._lost_frames = 0
