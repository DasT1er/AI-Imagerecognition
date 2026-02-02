"""
Transparent in-game overlay using tkinter.
Draws FOV circle, bounding boxes, crosshair, target info directly on screen.
No pygame - runs as a tkinter Toplevel from the main thread.
"""
import tkinter as tk
from typing import List, Tuple, Optional


class GameOverlay:
    """Transparent fullscreen overlay using tkinter Canvas."""

    TRANSPARENT_COLOR = "#000001"  # Color key for transparency

    def __init__(self, root: tk.Tk, config):
        self.config = config
        self.root = root
        self.window: Optional[tk.Toplevel] = None
        self.canvas: Optional[tk.Canvas] = None
        self._visible = False
        self._screen_w = 0
        self._screen_h = 0
        self._items = []  # Track canvas item IDs for clearing

    def create(self):
        """Create the transparent overlay window."""
        import sys

        self._screen_w = self.root.winfo_screenwidth()
        self._screen_h = self.root.winfo_screenheight()

        self.window = tk.Toplevel(self.root)
        self.window.title("overlay")
        self.window.geometry(f"{self._screen_w}x{self._screen_h}+0+0")
        self.window.overrideredirect(True)         # No window frame
        self.window.attributes("-topmost", True)    # Always on top

        if sys.platform == "win32":
            self.window.attributes("-transparentcolor", self.TRANSPARENT_COLOR)
            self.window.config(bg=self.TRANSPARENT_COLOR)

            # Ensure window is fully mapped before setting extended styles
            self.window.update_idletasks()
            self.window.update()

            # Make click-through on Windows
            try:
                import ctypes
                from ctypes import wintypes

                user32 = ctypes.windll.user32
                GWL_EXSTYLE = -20
                WS_EX_LAYERED = 0x00080000
                WS_EX_TRANSPARENT = 0x00000020
                WS_EX_TOOLWINDOW = 0x00000080

                # Use winfo_id() for reliable HWND retrieval
                hwnd = self.window.winfo_id()

                style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                style |= WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW
                user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

                # Force Windows to re-read the style
                user32.SetWindowPos(
                    hwnd, -1,  # HWND_TOPMOST
                    0, 0, self._screen_w, self._screen_h,
                    0x0020 | 0x0002  # SWP_FRAMECHANGED | SWP_NOMOVE (reapply styles)
                )
                self._click_through = True
            except Exception as e:
                print(f"[!] Overlay click-through failed: {e}")
                print("[!] Overlay disabled to prevent mouse blocking")
                self._click_through = False
                self.window.destroy()
                self.window = None
                self._visible = False
                return
        else:
            # Linux/macOS - tkinter overlays block input, skip overlay entirely
            print("[!] Game overlay not supported on this platform (no click-through)")
            self.window.destroy()
            self.window = None
            self._visible = False
            return

        self.canvas = tk.Canvas(
            self.window,
            width=self._screen_w,
            height=self._screen_h,
            bg=self.TRANSPARENT_COLOR,
            highlightthickness=0,
        )
        self.canvas.pack()
        self._visible = True

    def update(self, detections: list, capture_offset: Tuple[int, int],
               screen_center: Tuple[int, int], target=None,
               fps: float = 0.0, inference_ms: float = 0.0,
               enabled: bool = True):
        """
        Clear and redraw all overlay elements.
        Called from the main tkinter thread via after().
        """
        if not self._visible or self.canvas is None:
            return

        # Clear previous drawings
        self.canvas.delete("all")

        cfg = self.config
        if not cfg["overlay_enabled"]:
            return

        cx, cy = screen_center

        # FOV circle
        if cfg["show_fov_circle"]:
            r = int(cfg["fov_radius"])
            fov_color = self._rgb_to_hex(cfg["fov_color"])
            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                outline=fov_color, width=1
            )

        # Bounding boxes
        if cfg["show_bounding_boxes"]:
            box_color = self._rgb_to_hex(cfg["box_color"])
            for det in detections:
                sx1 = int(det.x1 + capture_offset[0])
                sy1 = int(det.y1 + capture_offset[1])
                sx2 = int(det.x2 + capture_offset[0])
                sy2 = int(det.y2 + capture_offset[1])
                w = sx2 - sx1
                h = sy2 - sy1

                # Corner-style box
                cl = max(8, min(w, h) // 4)
                self._draw_corner_box(sx1, sy1, sx2, sy2, cl, box_color)

                # Confidence label
                label = f"{det.confidence:.0%} {det.class_name}"
                self.canvas.create_text(
                    sx1, sy1 - 8, text=label, fill=box_color,
                    font=("Consolas", 10), anchor="w"
                )

        # Snaplines
        if cfg["show_snaplines"] and detections:
            snap_color = self._rgb_to_hex(cfg["snapline_color"])
            for det in detections:
                tx = int(det.center[0] + capture_offset[0])
                ty = int(det.y2 + capture_offset[1])
                self.canvas.create_line(
                    cx, self._screen_h, tx, ty,
                    fill=snap_color, width=1
                )

        # Crosshair
        if cfg["show_crosshair"]:
            ch_color = self._rgb_to_hex(cfg["crosshair_color"])
            size = 8
            gap = 3
            self.canvas.create_line(cx - size - gap, cy, cx - gap, cy,
                                     fill=ch_color, width=1)
            self.canvas.create_line(cx + gap, cy, cx + size + gap, cy,
                                     fill=ch_color, width=1)
            self.canvas.create_line(cx, cy - size - gap, cx, cy - gap,
                                     fill=ch_color, width=1)
            self.canvas.create_line(cx, cy + gap, cx, cy + size + gap,
                                     fill=ch_color, width=1)

        # Target highlight
        if target is not None and hasattr(target, "screen_point"):
            tx, ty = int(target.screen_point[0]), int(target.screen_point[1])
            self.canvas.create_oval(
                tx - 5, ty - 5, tx + 5, ty + 5,
                outline="#ff0000", width=2
            )
            # Small cross on aim point
            self.canvas.create_line(tx - 7, ty, tx + 7, ty,
                                     fill="#ffff00", width=1)
            self.canvas.create_line(tx, ty - 7, tx, ty + 7,
                                     fill="#ffff00", width=1)

        # Info text (top-left)
        if cfg["show_fps"]:
            status = "ON" if enabled else "OFF"
            s_color = "#55ff55" if enabled else "#ff5555"
            y = 10
            self.canvas.create_text(
                12, y, text=f"Aimbot: {status}", fill=s_color,
                font=("Consolas", 13, "bold"), anchor="w"
            )
            y += 20
            self.canvas.create_text(
                12, y, text=f"FPS: {fps:.0f}  |  Inference: {inference_ms:.1f}ms",
                fill="#cccccc", font=("Consolas", 11), anchor="w"
            )
            y += 18
            self.canvas.create_text(
                12, y, text=f"Targets: {len(detections)}  |  FOV: {cfg['fov_radius']}px",
                fill="#cccccc", font=("Consolas", 11), anchor="w"
            )

        # Target lock info
        if cfg["show_target_info"] and target is not None:
            info = (f"LOCKED: {target.detection.class_name} "
                    f"({target.detection.confidence:.0%}) "
                    f"dist={target.distance_to_crosshair:.0f}px")
            self.canvas.create_text(
                12, 70, text=info, fill="#ffcc33",
                font=("Consolas", 11, "bold"), anchor="w"
            )

    def _draw_corner_box(self, x1, y1, x2, y2, cl, color):
        """Draw corner-style bounding box."""
        c = self.canvas
        w = 2
        # Top-left
        c.create_line(x1, y1, x1 + cl, y1, fill=color, width=w)
        c.create_line(x1, y1, x1, y1 + cl, fill=color, width=w)
        # Top-right
        c.create_line(x2, y1, x2 - cl, y1, fill=color, width=w)
        c.create_line(x2, y1, x2, y1 + cl, fill=color, width=w)
        # Bottom-left
        c.create_line(x1, y2, x1 + cl, y2, fill=color, width=w)
        c.create_line(x1, y2, x1, y2 - cl, fill=color, width=w)
        # Bottom-right
        c.create_line(x2, y2, x2 - cl, y2, fill=color, width=w)
        c.create_line(x2, y2, x2, y2 - cl, fill=color, width=w)

    @staticmethod
    def _rgb_to_hex(rgb_list) -> str:
        """Convert [r, g, b] to #rrggbb hex color."""
        r, g, b = int(rgb_list[0]), int(rgb_list[1]), int(rgb_list[2])
        # Avoid exact transparent color
        if r == 0 and g == 0 and b <= 1:
            b = 2
        return f"#{r:02x}{g:02x}{b:02x}"

    def show(self):
        if self.window:
            self.window.deiconify()
            self._visible = True

    def hide(self):
        if self.window:
            self.window.withdraw()
            self._visible = False

    def toggle(self):
        if self._visible:
            self.hide()
        else:
            self.show()

    def destroy(self):
        if self.window:
            self.window.destroy()
            self.window = None
            self._visible = False
