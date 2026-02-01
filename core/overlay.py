"""
Transparent overlay rendered with pygame on a borderless transparent window.
Shows: FOV circle, bounding boxes, snaplines, crosshair, FPS, target info.
"""
import pygame
import win32api
import win32con
import win32gui
import ctypes
from typing import List, Tuple, Optional

from core.detector import Detection


# Windows layered window constants
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOPMOST = 0x00000008
WS_EX_TOOLWINDOW = 0x00000080
GWL_EXSTYLE = -20
LWA_COLORKEY = 0x00000001


class Overlay:
    """Transparent fullscreen overlay using pygame + win32."""

    TRANSPARENT_COLOR = (0, 0, 0)  # Color key for transparency

    def __init__(self, config):
        self.config = config
        self.screen_w = 0
        self.screen_h = 0
        self.hwnd = None
        self.surface = None
        self.font = None
        self.font_small = None
        self._initialized = False

    def init(self):
        """Initialize pygame overlay window."""
        # Get screen size
        self.screen_w = win32api.GetSystemMetrics(0)
        self.screen_h = win32api.GetSystemMetrics(1)

        # Init pygame with no frame
        pygame.init()
        self.surface = pygame.display.set_mode(
            (self.screen_w, self.screen_h),
            pygame.NOFRAME
        )
        pygame.display.set_caption("overlay")

        self.font = pygame.font.SysFont("Consolas", 16)
        self.font_small = pygame.font.SysFont("Consolas", 12)

        # Get window handle
        self.hwnd = pygame.display.get_wm_info()["window"]

        # Make window transparent, topmost, click-through
        style = win32gui.GetWindowLong(self.hwnd, GWL_EXSTYLE)
        style |= WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOPMOST | WS_EX_TOOLWINDOW
        win32gui.SetWindowLong(self.hwnd, GWL_EXSTYLE, style)

        # Set color key for transparency (black = transparent)
        win32gui.SetLayeredWindowAttributes(
            self.hwnd, 0x00000000, 0, LWA_COLORKEY
        )

        # Move to top-left, ensure fullscreen coverage
        win32gui.SetWindowPos(
            self.hwnd, win32con.HWND_TOPMOST,
            0, 0, self.screen_w, self.screen_h,
            win32con.SWP_SHOWWINDOW
        )

        self._initialized = True

    def render(self, detections: List[Detection],
               capture_offset: Tuple[int, int],
               screen_center: Tuple[int, int],
               target: Optional[object] = None,
               fps: float = 0.0,
               inference_ms: float = 0.0,
               enabled: bool = True):
        """Render one overlay frame."""
        if not self._initialized:
            return

        cfg = self.config
        self.surface.fill(self.TRANSPARENT_COLOR)

        if not cfg["overlay_enabled"]:
            pygame.display.flip()
            return

        cx, cy = screen_center

        # FOV circle
        if cfg["show_fov_circle"]:
            color = tuple(cfg["fov_color"])
            pygame.draw.circle(
                self.surface, color, (cx, cy),
                int(cfg["fov_radius"]), 1
            )

        # Bounding boxes
        if cfg["show_bounding_boxes"]:
            box_color = tuple(cfg["box_color"])
            for det in detections:
                sx1 = int(det.x1 + capture_offset[0])
                sy1 = int(det.y1 + capture_offset[1])
                sx2 = int(det.x2 + capture_offset[0])
                sy2 = int(det.y2 + capture_offset[1])
                w = sx2 - sx1
                h = sy2 - sy1

                # Corner-style box (looks cleaner)
                corner_len = max(8, min(w, h) // 4)
                self._draw_corner_box(
                    self.surface, box_color, sx1, sy1, w, h, corner_len, 2
                )

                # Confidence label
                label = f"{det.confidence:.0%}"
                text = self.font_small.render(label, True, box_color)
                self.surface.blit(text, (sx1, sy1 - 14))

        # Snaplines
        if cfg["show_snaplines"] and detections:
            snap_color = tuple(cfg["snapline_color"])
            for det in detections:
                target_x = int(det.center[0] + capture_offset[0])
                target_y = int(det.y2 + capture_offset[1])
                pygame.draw.line(
                    self.surface, snap_color,
                    (cx, self.screen_h), (target_x, target_y), 1
                )

        # Crosshair
        if cfg["show_crosshair"]:
            ch_color = tuple(cfg["crosshair_color"])
            size = 6
            gap = 3
            thickness = 1
            # Four lines around center with gap
            pygame.draw.line(self.surface, ch_color,
                             (cx - size - gap, cy), (cx - gap, cy), thickness)
            pygame.draw.line(self.surface, ch_color,
                             (cx + gap, cy), (cx + size + gap, cy), thickness)
            pygame.draw.line(self.surface, ch_color,
                             (cx, cy - size - gap), (cx, cy - gap), thickness)
            pygame.draw.line(self.surface, ch_color,
                             (cx, cy + gap), (cx, cy + size + gap), thickness)

        # Target highlight
        if target is not None and hasattr(target, "screen_point"):
            tx, ty = int(target.screen_point[0]), int(target.screen_point[1])
            pygame.draw.circle(self.surface, (255, 0, 0), (tx, ty), 4, 2)

        # Info text (top-left)
        y_offset = 10
        if cfg["show_fps"]:
            status = "ON" if enabled else "OFF"
            status_color = (0, 255, 0) if enabled else (255, 80, 80)
            texts = [
                (f"Aimbot: {status}", status_color),
                (f"FPS: {fps:.0f}  |  Inference: {inference_ms:.1f}ms", (200, 200, 200)),
                (f"Targets: {len(detections)}  |  FOV: {cfg['fov_radius']}px", (200, 200, 200)),
                (f"Bone: {cfg['target_bone']}  |  Smooth: {cfg['smoothing']:.2f}", (200, 200, 200)),
            ]
            for text_str, color in texts:
                text = self.font.render(text_str, True, color)
                # Draw shadow
                shadow = self.font.render(text_str, True, (30, 30, 30))
                self.surface.blit(shadow, (12, y_offset + 1))
                self.surface.blit(text, (11, y_offset))
                y_offset += 20

        if cfg["show_target_info"] and target is not None:
            info = (
                f"Locked: {target.detection.class_name} "
                f"({target.detection.confidence:.0%}) "
                f"dist={target.distance_to_crosshair:.0f}px"
            )
            text = self.font.render(info, True, (255, 200, 50))
            shadow = self.font.render(info, True, (30, 30, 30))
            self.surface.blit(shadow, (12, y_offset + 1))
            self.surface.blit(text, (11, y_offset))

        pygame.display.flip()

    def _draw_corner_box(self, surface, color, x, y, w, h,
                         corner_len, thickness):
        """Draw a box with only corner lines (cleaner look)."""
        # Top-left
        pygame.draw.line(surface, color, (x, y), (x + corner_len, y), thickness)
        pygame.draw.line(surface, color, (x, y), (x, y + corner_len), thickness)
        # Top-right
        pygame.draw.line(surface, color, (x + w, y), (x + w - corner_len, y), thickness)
        pygame.draw.line(surface, color, (x + w, y), (x + w, y + corner_len), thickness)
        # Bottom-left
        pygame.draw.line(surface, color, (x, y + h), (x + corner_len, y + h), thickness)
        pygame.draw.line(surface, color, (x, y + h), (x, y + h - corner_len), thickness)
        # Bottom-right
        pygame.draw.line(surface, color, (x + w, y + h), (x + w - corner_len, y + h), thickness)
        pygame.draw.line(surface, color, (x + w, y + h), (x + w, y + h - corner_len), thickness)

    def process_events(self) -> bool:
        """Process pygame events. Returns False if should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def destroy(self):
        """Clean up overlay."""
        if self._initialized:
            pygame.quit()
            self._initialized = False
