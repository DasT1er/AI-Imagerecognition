"""
Triggerbot: automatically fires when crosshair is on an enemy.
Supports head-only mode, configurable crosshair area, burst control.
"""
import time
import random
from typing import List, Tuple

from core.detector import Detection


class Triggerbot:
    """Fires when crosshair overlaps with a detected enemy."""

    def __init__(self, config):
        self.config = config
        self._last_trigger_time = 0.0
        self._trigger_delay = 0.0
        self._waiting = False
        self._burst_shots = 0
        self._burst_start = 0.0

    def check_trigger(self, detections: List[Detection],
                      screen_center: Tuple[int, int],
                      capture_offset: Tuple[int, int]) -> bool:
        """
        Check if crosshair is on an enemy bbox.
        Returns True if should fire.
        """
        cfg = self.config
        if not cfg["triggerbot_enabled"]:
            return False

        now = time.perf_counter()

        # Burst cooldown: limit rapid firing
        burst_max = cfg.get("triggerbot_burst_max", 5)
        burst_window = cfg.get("triggerbot_burst_window", 0.5)
        if self._burst_shots >= burst_max:
            if now - self._burst_start < burst_window:
                return False
            self._burst_shots = 0

        # Crosshair position in local capture coords
        cx_local = screen_center[0] - capture_offset[0]
        cy_local = screen_center[1] - capture_offset[1]

        # Check margin around crosshair (pixels)
        margin = cfg.get("triggerbot_margin", 3)
        head_ids = set(cfg.get("head_class_ids", [1, 3]))
        head_only = cfg.get("triggerbot_head_only", False)

        on_target = False
        for det in detections:
            # Skip body detections if head-only mode
            if head_only and det.class_id not in head_ids:
                continue

            # Check if crosshair (+margin) is inside detection bbox
            if (det.x1 - margin <= cx_local <= det.x2 + margin and
                    det.y1 - margin <= cy_local <= det.y2 + margin):
                on_target = True
                break

        if on_target:
            if not self._waiting:
                # Start reaction delay
                self._waiting = True
                self._trigger_delay = random.uniform(
                    cfg["triggerbot_delay_min"] / 1000,
                    cfg["triggerbot_delay_max"] / 1000,
                )
                self._last_trigger_time = now
                return False
            else:
                if now - self._last_trigger_time >= self._trigger_delay:
                    self._waiting = False
                    # Track burst
                    if self._burst_shots == 0:
                        self._burst_start = now
                    self._burst_shots += 1
                    return True
                return False
        else:
            self._waiting = False
            return False
