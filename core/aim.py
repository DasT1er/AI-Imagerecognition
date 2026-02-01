"""
Aim engine: target selection, smooth aiming, prediction, humanization.
"""
import math
import time
import random
from typing import List, Optional, Tuple
from dataclasses import dataclass, field

from core.detector import Detection
from utils.math_utils import (
    distance, calculate_move_delta, add_jitter,
    predict_position, clamp, generate_bezier_path,
)


@dataclass
class TrackedTarget:
    """Target with velocity tracking for prediction."""
    detection: Detection
    aim_point: Tuple[float, float]
    screen_point: Tuple[float, float]  # Aim point in screen coordinates
    distance_to_crosshair: float
    velocity: Tuple[float, float] = (0.0, 0.0)
    last_seen: float = 0.0


class AimEngine:
    """Handles target selection, aim calculation, and smooth movement."""

    def __init__(self, config):
        self.config = config
        self._prev_targets: dict = {}  # class_id+position hash -> TrackedTarget
        self._current_target: Optional[TrackedTarget] = None
        self._last_aim_time = 0.0
        self._flick_path: list = []
        self._flick_index = 0

    def select_target(self, detections: List[Detection],
                      screen_center: Tuple[int, int],
                      capture_offset: Tuple[int, int]) -> Optional[TrackedTarget]:
        """
        Select best target from detections.
        Converts detection coords (relative to capture region) to screen coords.
        """
        if not detections:
            self._current_target = None
            return None

        cfg = self.config
        fov = cfg["fov_radius"]
        bone = cfg["target_bone"]
        sort_mode = cfg["target_sort"]
        now = time.perf_counter()

        candidates = []
        for det in detections:
            # Get aim point in capture-region coordinates
            aim_local = det.get_aim_point(
                bone=bone,
                head_r=cfg["head_ratio"],
                neck_r=cfg["neck_ratio"],
                chest_r=cfg["chest_ratio"],
                body_r=cfg["body_ratio"],
            )

            # Convert to screen coordinates
            aim_screen = (
                aim_local[0] + capture_offset[0],
                aim_local[1] + capture_offset[1],
            )

            dist = distance(screen_center, aim_screen)

            # FOV check
            if dist > fov:
                continue

            # Track velocity
            target_key = f"{det.class_id}_{int(det.center[0]//20)}_{int(det.center[1]//20)}"
            velocity = (0.0, 0.0)
            if target_key in self._prev_targets:
                prev = self._prev_targets[target_key]
                dt = now - prev.last_seen
                if 0 < dt < 0.5:  # Only track if recent
                    velocity = (
                        (aim_screen[0] - prev.screen_point[0]) / dt,
                        (aim_screen[1] - prev.screen_point[1]) / dt,
                    )

            tracked = TrackedTarget(
                detection=det,
                aim_point=aim_local,
                screen_point=aim_screen,
                distance_to_crosshair=dist,
                velocity=velocity,
                last_seen=now,
            )
            candidates.append(tracked)
            self._prev_targets[target_key] = tracked

        if not candidates:
            self._current_target = None
            return None

        # Sort candidates
        if sort_mode == "distance":
            candidates.sort(key=lambda t: t.distance_to_crosshair)
        elif sort_mode == "confidence":
            candidates.sort(key=lambda t: -t.detection.confidence)
        elif sort_mode == "area":
            candidates.sort(key=lambda t: -t.detection.area)

        # Sticky targeting: prefer current target if still visible
        if self._current_target is not None:
            for c in candidates:
                prev_screen = self._current_target.screen_point
                if distance(prev_screen, c.screen_point) < 50:
                    self._current_target = c
                    return c

        self._current_target = candidates[0]
        return candidates[0]

    def compute_move(self, target: TrackedTarget,
                     screen_center: Tuple[int, int]) -> Tuple[int, int]:
        """
        Compute mouse move delta (dx, dy) to move towards target.
        Applies smoothing, humanization, prediction.
        """
        cfg = self.config
        aim_point = target.screen_point

        # Prediction
        if cfg["prediction_enabled"] and (
            abs(target.velocity[0]) > 5 or abs(target.velocity[1]) > 5
        ):
            aim_point = predict_position(
                aim_point, target.velocity, cfg["prediction_factor"]
            )

        # Check for flick
        dist = distance(screen_center, aim_point)

        if cfg["flick_enabled"] and dist < cfg["flick_threshold"]:
            # Close target: fast flick
            dx = aim_point[0] - screen_center[0]
            dy = aim_point[1] - screen_center[1]
            if cfg["humanize"]:
                dx, dy = add_jitter(dx, dy, cfg["humanize_jitter"] * 0.5)
            return (int(round(dx)), int(round(dy)))

        # Smooth movement
        dx, dy = calculate_move_delta(
            current=screen_center,
            target=aim_point,
            smoothing=cfg["smoothing"],
            curve=cfg["smoothing_curve"],
            max_move=cfg["max_move_per_tick"],
        )

        # Humanize
        if cfg["humanize"]:
            dx, dy = add_jitter(dx, dy, cfg["humanize_jitter"])

            # Random micro-delay
            delay_min = cfg["humanize_delay_min"] / 1000
            delay_max = cfg["humanize_delay_max"] / 1000
            if delay_max > delay_min:
                time.sleep(random.uniform(delay_min, delay_max))

        return (int(round(dx)), int(round(dy)))

    def is_on_target(self, target: TrackedTarget,
                     screen_center: Tuple[int, int],
                     threshold: float = 5.0) -> bool:
        """Check if crosshair is close enough to target."""
        return distance(screen_center, target.screen_point) < threshold

    def reset(self):
        """Reset aim state."""
        self._current_target = None
        self._prev_targets.clear()
        self._flick_path.clear()
