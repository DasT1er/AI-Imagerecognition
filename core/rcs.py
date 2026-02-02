"""
Recoil Control System (RCS) for CS2.
Applies downward mouse compensation while firing to counter weapon recoil.
Uses a simple spray pattern: mostly vertical pull-down with slight horizontal.
"""
import time
import math


class RecoilControl:
    """Compensates for weapon recoil during sustained fire."""

    # Approximate CS2 spray pattern (first 30 bullets, normalized offsets)
    # Each entry = (dx, dy) as fraction of max recoil per tick
    # Positive dy = downward recoil (we compensate by moving mouse DOWN)
    SPRAY_PATTERN = [
        (0.0, 0.4), (0.0, 0.6), (0.0, 0.8), (0.0, 1.0), (0.0, 1.0),
        (-0.1, 1.0), (-0.2, 0.9), (-0.3, 0.8), (-0.3, 0.7), (-0.2, 0.6),
        (0.1, 0.6), (0.3, 0.5), (0.4, 0.5), (0.3, 0.4), (0.1, 0.4),
        (-0.1, 0.4), (-0.3, 0.5), (-0.4, 0.5), (-0.3, 0.4), (-0.1, 0.4),
        (0.2, 0.3), (0.3, 0.3), (0.3, 0.3), (0.2, 0.3), (0.0, 0.3),
        (-0.2, 0.3), (-0.3, 0.3), (-0.3, 0.3), (-0.2, 0.3), (0.0, 0.3),
    ]

    def __init__(self, config):
        self.config = config
        self._firing = False
        self._fire_start = 0.0
        self._shot_index = 0
        self._last_tick = 0.0

    def update(self, is_firing: bool) -> tuple:
        """
        Call every frame. Returns (dx, dy) mouse compensation to apply.
        is_firing: True if the player is currently holding fire.
        """
        cfg = self.config
        if not cfg.get("rcs_enabled", False):
            if self._firing:
                self._reset()
            return (0, 0)

        now = time.perf_counter()

        if is_firing:
            if not self._firing:
                # Just started firing
                self._firing = True
                self._fire_start = now
                self._shot_index = 0
                self._last_tick = now
                return (0, 0)

            # Estimate which shot we're on (~600 RPM = 100ms per shot)
            fire_rate_ms = cfg.get("rcs_fire_rate_ms", 100)
            elapsed = now - self._fire_start
            new_index = int(elapsed / (fire_rate_ms / 1000))

            if new_index <= self._shot_index:
                return (0, 0)  # Same shot, no new compensation

            self._shot_index = new_index

            # Get spray pattern offset
            idx = min(self._shot_index, len(self.SPRAY_PATTERN) - 1)
            pattern_x, pattern_y = self.SPRAY_PATTERN[idx]

            # Apply strength multipliers
            strength_x = cfg.get("rcs_strength_x", 0.5)
            strength_y = cfg.get("rcs_strength_y", 0.5)

            # Scale: rcs_pull is how many pixels to move per shot at max recoil
            pull = cfg.get("rcs_pull_per_shot", 4.0)

            dx = pattern_x * pull * strength_x
            dy = -pattern_y * pull * strength_y  # Negative = move mouse DOWN

            return (int(round(dx)), int(round(dy)))
        else:
            if self._firing:
                self._reset()
            return (0, 0)

    def _reset(self):
        self._firing = False
        self._shot_index = 0
        self._fire_start = 0.0
