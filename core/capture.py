"""
High-performance screen capture using mss.
Captures a region around the center of the screen for detection.
"""
import numpy as np
import mss
import mss.tools


class ScreenCapture:
    """Fast screen grabber that captures a centered region."""

    def __init__(self, width: int = 640, height: int = 640, monitor_index: int = 1):
        self.sct = mss.mss()
        self.monitor_index = monitor_index
        self.capture_width = width
        self.capture_height = height
        self._update_region()

    def _update_region(self):
        monitor = self.sct.monitors[self.monitor_index]
        self.screen_width = monitor["width"]
        self.screen_height = monitor["height"]
        self.center_x = monitor["left"] + self.screen_width // 2
        self.center_y = monitor["top"] + self.screen_height // 2

        self.region = {
            "left": self.center_x - self.capture_width // 2,
            "top": self.center_y - self.capture_height // 2,
            "width": self.capture_width,
            "height": self.capture_height,
        }

    def set_region_size(self, width: int, height: int):
        self.capture_width = width
        self.capture_height = height
        self._update_region()

    def grab(self) -> np.ndarray:
        """Capture screen region and return as BGR numpy array."""
        raw = self.sct.grab(self.region)
        # mss returns BGRA, convert to BGR for OpenCV/YOLO
        frame = np.array(raw, dtype=np.uint8)[:, :, :3]
        return frame

    def grab_full(self) -> np.ndarray:
        """Capture the full screen."""
        monitor = self.sct.monitors[self.monitor_index]
        raw = self.sct.grab(monitor)
        frame = np.array(raw, dtype=np.uint8)[:, :, :3]
        return frame

    @property
    def offset(self) -> tuple:
        """Return (offset_x, offset_y) of capture region relative to screen."""
        return (self.region["left"], self.region["top"])
