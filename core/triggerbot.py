"""
Triggerbot: automatically fires when crosshair is on an enemy.
"""
import time
import random
from typing import List, Tuple

from core.detector import Detection


class Triggerbot:
    """Fires when crosshair overlaps with a detected enemy bounding box."""

    def __init__(self, config):
        self.config = config
        self._last_trigger_time = 0.0
        self._trigger_delay = 0.0
        self._waiting = False

    def check_trigger(self, detections: List[Detection],
                      screen_center: Tuple[int, int],
                      capture_offset: Tuple[int, int]) -> bool:
        """
        Check if any detection bbox contains the screen center (crosshair).
        Returns True if should fire.
        """
        cfg = self.config
        if not cfg["triggerbot_enabled"]:
            return False

        now = time.perf_counter()
        crosshair_local = (
            screen_center[0] - capture_offset[0],
            screen_center[1] - capture_offset[1],
        )

        on_target = False
        for det in detections:
            if (det.x1 <= crosshair_local[0] <= det.x2 and
                    det.y1 <= crosshair_local[1] <= det.y2):
                on_target = True
                break

        if on_target:
            if not self._waiting:
                # Start delay timer
                self._waiting = True
                self._trigger_delay = random.uniform(
                    cfg["triggerbot_delay_min"] / 1000,
                    cfg["triggerbot_delay_max"] / 1000,
                )
                self._last_trigger_time = now
                return False
            else:
                # Check if delay has elapsed
                if now - self._last_trigger_time >= self._trigger_delay:
                    self._waiting = False
                    return True
                return False
        else:
            self._waiting = False
            return False
