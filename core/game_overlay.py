"""
Transparent in-game overlay using tkinter + Win32 API.
Uses SetLayeredWindowAttributes for reliable color-key transparency
and WS_EX_TRANSPARENT for click-through.
"""
import sys
import tkinter as tk
from typing import Tuple, Optional


class GameOverlay:
    """Transparent fullscreen overlay - Windows only."""

    # Bright magenta as chroma key - won't be altered by color management
    # and won't appear in normal game footage or overlay drawings
    CHROMA_KEY = "#ff00ff"
    CHROMA_COLORREF = 0x00FF00FF  # Win32 COLORREF (0x00BBGGRR)

    def __init__(self, root: tk.Tk, config):
        self.config = config
        self.root = root
        self.window: Optional[tk.Toplevel] = None
        self.canvas: Optional[tk.Canvas] = None
        self._visible = False
        self._screen_w = 0
        self._screen_h = 0

    def create(self):
        """Create the transparent overlay window."""
        if sys.platform != "win32":
            print("[!] Game overlay only works on Windows")
            return

        self._screen_w = self.root.winfo_screenwidth()
        self._screen_h = self.root.winfo_screenheight()

        # Create toplevel window
        self.window = tk.Toplevel(self.root)
        self.window.title("")
        self.window.overrideredirect(True)
        self.window.geometry(f"{self._screen_w}x{self._screen_h}+0+0")
        self.window.config(bg=self.CHROMA_KEY)

        # Create canvas
        self.canvas = tk.Canvas(
            self.window,
            width=self._screen_w,
            height=self._screen_h,
            bg=self.CHROMA_KEY,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.place(x=0, y=0)

        # Must render first so Windows creates the actual HWND
        self.window.update_idletasks()
        self.window.update()

        # Apply Win32 transparency + click-through
        try:
            self._setup_win32()
        except Exception as e:
            print(f"[!] Overlay Win32 setup failed: {e}")
            import traceback
            traceback.print_exc()
            self.window.destroy()
            self.window = None
            self.canvas = None
            self._visible = False
            return

        self._visible = True
        print("[+] Game overlay active")

    def _setup_win32(self):
        """Apply Win32 layered window + click-through using ctypes."""
        import ctypes
        import ctypes.wintypes as wt

        user32 = ctypes.windll.user32

        # Constants
        GWL_EXSTYLE = -20
        WS_EX_LAYERED = 0x00080000
        WS_EX_TRANSPARENT = 0x00000020
        WS_EX_TOOLWINDOW = 0x00000080
        WS_EX_NOACTIVATE = 0x08000000
        LWA_COLORKEY = 0x00000001
        GA_ROOT = 2
        HWND_TOPMOST = -1
        SWP_NOMOVE = 0x0002
        SWP_NOSIZE = 0x0001
        SWP_NOACTIVATE = 0x0010

        # --- Step 1: Find the correct top-level HWND ---
        # winfo_id() returns the child widget. We need the actual window.
        child_hwnd = self.window.winfo_id()

        user32.GetAncestor.restype = wt.HWND
        user32.GetAncestor.argtypes = [wt.HWND, ctypes.c_uint]
        top_hwnd = user32.GetAncestor(child_hwnd, GA_ROOT)

        if not top_hwnd:
            # Fallback
            try:
                top_hwnd = int(self.window.frame(), 16)
            except Exception:
                top_hwnd = child_hwnd

        print(f"    HWND: child=0x{child_hwnd:08X} top=0x{top_hwnd:08X}")

        # --- Step 2: Set extended window styles ---
        style = user32.GetWindowLongW(top_hwnd, GWL_EXSTYLE)
        print(f"    Style before: 0x{style:08X}")

        new_style = style | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE
        result = user32.SetWindowLongW(top_hwnd, GWL_EXSTYLE, new_style)

        verify = user32.GetWindowLongW(top_hwnd, GWL_EXSTYLE)
        print(f"    Style after:  0x{verify:08X}")

        if not (verify & WS_EX_LAYERED):
            raise RuntimeError("Failed to set WS_EX_LAYERED")
        if not (verify & WS_EX_TRANSPARENT):
            raise RuntimeError("Failed to set WS_EX_TRANSPARENT")

        # --- Step 3: Set color key transparency via Win32 API directly ---
        # This bypasses tkinter's -transparentcolor entirely
        user32.SetLayeredWindowAttributes.argtypes = [
            wt.HWND, wt.COLORREF, wt.BYTE, wt.DWORD
        ]
        user32.SetLayeredWindowAttributes.restype = wt.BOOL
        ok = user32.SetLayeredWindowAttributes(
            top_hwnd,
            self.CHROMA_COLORREF,  # Color key: magenta
            0,                      # Alpha (unused with LWA_COLORKEY)
            LWA_COLORKEY,           # Use color key mode
        )
        if not ok:
            raise RuntimeError("SetLayeredWindowAttributes failed")

        print(f"    Color key: {self.CHROMA_KEY} (COLORREF=0x{self.CHROMA_COLORREF:08X})")

        # --- Step 4: Ensure topmost ---
        user32.SetWindowPos(
            top_hwnd, HWND_TOPMOST,
            0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
        )

        print("    Click-through: OK")

    # ──────────────── Drawing ────────────────

    def update(self, detections: list, capture_offset: Tuple[int, int],
               screen_center: Tuple[int, int], target=None,
               fps: float = 0.0, inference_ms: float = 0.0,
               enabled: bool = True):
        """Redraw overlay. Called from tkinter main thread."""
        if not self._visible or self.canvas is None:
            return

        self.canvas.delete("all")

        cfg = self.config
        if not cfg["overlay_enabled"]:
            return

        cx, cy = screen_center
        head_ids = set(cfg.get("head_class_ids", [1, 3]))

        # FOV circle
        if cfg["show_fov_circle"]:
            r = int(cfg["fov_radius"])
            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                outline=self._color(cfg["fov_color"]), width=1
            )

        # Bounding boxes
        if cfg["show_bounding_boxes"]:
            box_col = self._color(cfg["box_color"])
            head_col = self._color(cfg.get("head_box_color", [0, 255, 255]))
            for det in detections:
                sx1 = int(det.x1 + capture_offset[0])
                sy1 = int(det.y1 + capture_offset[1])
                sx2 = int(det.x2 + capture_offset[0])
                sy2 = int(det.y2 + capture_offset[1])
                is_head = det.class_id in head_ids
                col = head_col if is_head else box_col

                w = sx2 - sx1
                h = sy2 - sy1
                cl = max(8, min(w, h) // 4)
                self._corners(sx1, sy1, sx2, sy2, cl, col)

                label = f"{det.confidence:.0%} {det.class_name}"
                self.canvas.create_text(
                    sx1, sy1 - 8, text=label, fill=col,
                    font=("Consolas", 10), anchor="w"
                )

        # Snaplines
        if cfg["show_snaplines"] and detections:
            sc = self._color(cfg["snapline_color"])
            for det in detections:
                tx = int(det.center[0] + capture_offset[0])
                ty = int(det.y2 + capture_offset[1])
                self.canvas.create_line(cx, self._screen_h, tx, ty, fill=sc, width=1)

        # Crosshair
        if cfg["show_crosshair"]:
            cc = self._color(cfg["crosshair_color"])
            s, g = 8, 3
            self.canvas.create_line(cx-s-g, cy, cx-g, cy, fill=cc, width=1)
            self.canvas.create_line(cx+g, cy, cx+s+g, cy, fill=cc, width=1)
            self.canvas.create_line(cx, cy-s-g, cx, cy-g, fill=cc, width=1)
            self.canvas.create_line(cx, cy+g, cx, cy+s+g, fill=cc, width=1)

        # Target marker
        if target is not None and hasattr(target, "screen_point"):
            tx, ty = int(target.screen_point[0]), int(target.screen_point[1])
            self.canvas.create_oval(tx-5, ty-5, tx+5, ty+5, outline="#ff0000", width=2)
            self.canvas.create_line(tx-7, ty, tx+7, ty, fill="#ffff00", width=1)
            self.canvas.create_line(tx, ty-7, tx, ty+7, fill="#ffff00", width=1)

        # HUD info
        if cfg["show_fps"]:
            status = "ON" if enabled else "OFF"
            scol = "#55ff55" if enabled else "#ff5555"
            self.canvas.create_text(
                12, 10, text=f"Aimbot: {status}", fill=scol,
                font=("Consolas", 13, "bold"), anchor="w"
            )
            self.canvas.create_text(
                12, 30, text=f"FPS: {fps:.0f}  |  Inf: {inference_ms:.1f}ms",
                fill="#cccccc", font=("Consolas", 11), anchor="w"
            )
            self.canvas.create_text(
                12, 48, text=f"Targets: {len(detections)}  |  FOV: {cfg['fov_radius']}px",
                fill="#cccccc", font=("Consolas", 11), anchor="w"
            )

        if cfg["show_target_info"] and target is not None:
            info = (f"LOCKED: {target.detection.class_name} "
                    f"({target.detection.confidence:.0%}) "
                    f"dist={target.distance_to_crosshair:.0f}px")
            self.canvas.create_text(
                12, 70, text=info, fill="#ffcc33",
                font=("Consolas", 11, "bold"), anchor="w"
            )

    def _corners(self, x1, y1, x2, y2, cl, color):
        """Draw corner brackets around a bounding box."""
        c = self.canvas
        w = 2
        c.create_line(x1, y1, x1+cl, y1, fill=color, width=w)
        c.create_line(x1, y1, x1, y1+cl, fill=color, width=w)
        c.create_line(x2, y1, x2-cl, y1, fill=color, width=w)
        c.create_line(x2, y1, x2, y1+cl, fill=color, width=w)
        c.create_line(x1, y2, x1+cl, y2, fill=color, width=w)
        c.create_line(x1, y2, x1, y2-cl, fill=color, width=w)
        c.create_line(x2, y2, x2-cl, y2, fill=color, width=w)
        c.create_line(x2, y2, x2, y2-cl, fill=color, width=w)

    def _color(self, rgb) -> str:
        """Convert [r,g,b] to hex. Avoids chroma key color."""
        r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
        # If color matches chroma key exactly, shift it
        if r == 255 and g == 0 and b == 255:
            b = 254
        return f"#{r:02x}{g:02x}{b:02x}"

    # ──────────────── Visibility ────────────────

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
