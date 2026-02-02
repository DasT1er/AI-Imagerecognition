"""
Transparent in-game overlay using tkinter.
Draws FOV circle, bounding boxes, crosshair, target info directly on screen.
Uses Win32 API for proper click-through transparency on Windows.
"""
import sys
import tkinter as tk
from typing import List, Tuple, Optional


class GameOverlay:
    """Transparent fullscreen overlay using tkinter Canvas."""

    # Use a distinct color that won't appear in normal drawings
    TRANSPARENT_COLOR = "#010101"

    def __init__(self, root: tk.Tk, config):
        self.config = config
        self.root = root
        self.window: Optional[tk.Toplevel] = None
        self.canvas: Optional[tk.Canvas] = None
        self._visible = False
        self._screen_w = 0
        self._screen_h = 0
        self._click_through = False

    def create(self):
        """Create the transparent overlay window."""
        if sys.platform != "win32":
            print("[!] Game overlay not supported on this platform (no click-through)")
            return

        self._screen_w = self.root.winfo_screenwidth()
        self._screen_h = self.root.winfo_screenheight()

        self.window = tk.Toplevel(self.root)
        self.window.title("_overlay_")
        self.window.geometry(f"{self._screen_w}x{self._screen_h}+0+0")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)

        # Set transparent color BEFORE creating canvas
        self.window.attributes("-transparentcolor", self.TRANSPARENT_COLOR)
        self.window.config(bg=self.TRANSPARENT_COLOR)

        # Create canvas with same transparent background
        self.canvas = tk.Canvas(
            self.window,
            width=self._screen_w,
            height=self._screen_h,
            bg=self.TRANSPARENT_COLOR,
            highlightthickness=0,
            bd=0,
            relief="flat",
        )
        self.canvas.pack(fill="both", expand=True)

        # Force the window to fully render before touching Win32 styles
        self.window.update_idletasks()
        self.window.update()

        # Now apply click-through using Win32 API
        try:
            self._apply_click_through()
        except Exception as e:
            print(f"[!] Overlay click-through failed: {e}")
            import traceback
            traceback.print_exc()
            print("[!] Overlay disabled to prevent mouse blocking")
            self.window.destroy()
            self.window = None
            self.canvas = None
            self._visible = False
            return

        self._visible = True
        print("[+] Game overlay created successfully (click-through enabled)")

    def _apply_click_through(self):
        """Set Win32 extended window styles for click-through transparency."""
        import ctypes
        import ctypes.wintypes

        user32 = ctypes.windll.user32

        GWL_EXSTYLE = -20
        WS_EX_LAYERED = 0x00080000
        WS_EX_TRANSPARENT = 0x00000020
        WS_EX_TOOLWINDOW = 0x00000080
        WS_EX_NOACTIVATE = 0x08000000

        GA_ROOT = 2
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_FRAMECHANGED = 0x0020
        SWP_NOACTIVATE = 0x0010
        HWND_TOPMOST = -1

        # Get the actual top-level HWND (not the child widget)
        child_hwnd = self.window.winfo_id()

        # GetAncestor(GA_ROOT) walks up to the real top-level window
        user32.GetAncestor.restype = ctypes.wintypes.HWND
        user32.GetAncestor.argtypes = [ctypes.wintypes.HWND, ctypes.c_uint]
        top_hwnd = user32.GetAncestor(child_hwnd, GA_ROOT)

        if not top_hwnd:
            # Fallback: try parsing tkinter frame()
            try:
                top_hwnd = int(self.window.frame(), 16)
            except Exception:
                top_hwnd = child_hwnd

        print(f"    child_hwnd=0x{child_hwnd:08x}, top_hwnd=0x{top_hwnd:08x}")

        # Set extended styles on the TOP-LEVEL window
        # This is where -transparentcolor already set WS_EX_LAYERED
        style = user32.GetWindowLongW(top_hwnd, GWL_EXSTYLE)
        new_style = style | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE
        user32.SetWindowLongW(top_hwnd, GWL_EXSTYLE, new_style)

        # Verify style was set
        verify = user32.GetWindowLongW(top_hwnd, GWL_EXSTYLE)
        if not (verify & WS_EX_TRANSPARENT):
            raise RuntimeError(f"Failed to set WS_EX_TRANSPARENT (style=0x{verify:08x})")

        # Ask Windows to reapply without moving or resizing
        user32.SetWindowPos(
            top_hwnd,
            HWND_TOPMOST,
            0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_FRAMECHANGED | SWP_NOACTIVATE
        )

        self._click_through = True
        print(f"    Extended style: 0x{verify:08x} (click-through OK)")

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
        head_ids = set(cfg.get("head_class_ids", [1, 3]))

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
            head_color = self._rgb_to_hex(cfg.get("head_box_color", [255, 0, 255]))
            for det in detections:
                sx1 = int(det.x1 + capture_offset[0])
                sy1 = int(det.y1 + capture_offset[1])
                sx2 = int(det.x2 + capture_offset[0])
                sy2 = int(det.y2 + capture_offset[1])

                is_head = det.class_id in head_ids
                color = head_color if is_head else box_color

                # Corner-style box
                w = sx2 - sx1
                h = sy2 - sy1
                cl = max(8, min(w, h) // 4)
                self._draw_corner_box(sx1, sy1, sx2, sy2, cl, color)

                # Confidence label
                label = f"{det.confidence:.0%} {det.class_name}"
                self.canvas.create_text(
                    sx1, sy1 - 8, text=label, fill=color,
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
        # Avoid exact transparent color (#010101)
        if r <= 1 and g <= 1 and b <= 1:
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
            self.canvas = None
            self._visible = False
