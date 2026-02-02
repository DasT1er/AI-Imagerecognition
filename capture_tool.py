"""
CS2 Training Data Capture Tool

Standalone GUI tool for collecting screenshots from CS2 for YOLO labeling.
- Select monitor/screen
- Hotkey capture (F5) or auto-capture at interval
- Preview what's being captured
- Auto-save with incrementing filenames

Usage:
  python capture_tool.py
"""
import sys
import os
import time
import threading
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
import numpy as np
import cv2
from PIL import Image, ImageTk
import mss


class CaptureToolGUI(ctk.CTk):
    """Training data capture tool with GUI."""

    PREVIEW_W = 640
    PREVIEW_H = 360

    def __init__(self):
        super().__init__()

        self._lock = threading.Lock()
        self._preview_image = None
        self._capture_count = 0
        self._auto_running = False
        self._stop_event = threading.Event()
        self._preview_thread = None

        self._setup_window()
        self._build_ui()
        self._populate_monitors()
        self._update_preview_loop()
        self._start_live_preview()

    def _setup_window(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.title("CS2 Capture Tool - Training Data Collector")
        self.geometry("700x750")
        self.minsize(660, 700)

    def _build_ui(self):
        # === Preview ===
        prev_frame = ctk.CTkFrame(self, corner_radius=8)
        prev_frame.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(prev_frame, text="Live Preview",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=10, pady=(5, 0))

        self.preview_label = ctk.CTkLabel(prev_frame, text="No preview",
                                           width=self.PREVIEW_W,
                                           height=self.PREVIEW_H)
        self.preview_label.pack(padx=10, pady=10)

        # === Monitor + Output ===
        settings_frame = ctk.CTkFrame(self, corner_radius=8)
        settings_frame.pack(fill="x", padx=10, pady=5)

        row1 = ctk.CTkFrame(settings_frame, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=(8, 3))

        ctk.CTkLabel(row1, text="Monitor:").pack(side="left", padx=(0, 5))
        self.monitor_var = ctk.StringVar(value="1")
        self.monitor_dropdown = ctk.CTkOptionMenu(row1,
                                                    variable=self.monitor_var,
                                                    values=["1"],
                                                    width=220)
        self.monitor_dropdown.pack(side="left", padx=(0, 15))

        self.count_label = ctk.CTkLabel(row1, text="Captured: 0",
                                         font=ctk.CTkFont(size=13, weight="bold"),
                                         text_color="#55ff55")
        self.count_label.pack(side="right")

        # Output folder
        row2 = ctk.CTkFrame(settings_frame, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(row2, text="Output Folder:").pack(side="left", padx=(0, 5))
        self.output_entry = ctk.CTkEntry(row2, width=350)
        default_output = os.path.join(os.path.dirname(__file__), "training_data")
        self.output_entry.insert(0, default_output)
        self.output_entry.pack(side="left", padx=(0, 5))

        ctk.CTkButton(row2, text="Browse", width=70,
                       command=self._browse_output).pack(side="left")

        # Capture region
        row3 = ctk.CTkFrame(settings_frame, fg_color="transparent")
        row3.pack(fill="x", padx=10, pady=3)

        ctk.CTkLabel(row3, text="Capture:").pack(side="left", padx=(0, 5))

        self.capture_mode_var = ctk.StringVar(value="fullscreen")
        ctk.CTkOptionMenu(row3, variable=self.capture_mode_var,
                           values=["fullscreen", "center 640x640",
                                   "center 1280x720", "center 1920x1080"],
                           width=180).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(row3, text="Format:").pack(side="left", padx=(0, 5))
        self.format_var = ctk.StringVar(value="jpg")
        ctk.CTkOptionMenu(row3, variable=self.format_var,
                           values=["jpg", "png"],
                           width=80).pack(side="left")

        # Quality
        row3b = ctk.CTkFrame(settings_frame, fg_color="transparent")
        row3b.pack(fill="x", padx=10, pady=(3, 8))

        ctk.CTkLabel(row3b, text="JPG Quality:").pack(side="left", padx=(0, 5))
        self.quality_var = ctk.IntVar(value=95)
        self.quality_slider = ctk.CTkSlider(row3b, from_=50, to=100,
                                             variable=self.quality_var,
                                             width=150)
        self.quality_slider.pack(side="left", padx=(0, 5))
        self.quality_label = ctk.CTkLabel(row3b, text="95")
        self.quality_label.pack(side="left")

        self.quality_slider.configure(command=lambda v: self.quality_label.configure(
            text=str(int(float(v)))))

        # === Controls ===
        ctrl_frame = ctk.CTkFrame(self, corner_radius=8)
        ctrl_frame.pack(fill="x", padx=10, pady=5)

        ctrl_inner = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        ctrl_inner.pack(fill="x", padx=10, pady=8)

        self.btn_capture = ctk.CTkButton(ctrl_inner, text="Capture (F5)",
                                          fg_color="#2d8a4e", hover_color="#23713f",
                                          width=120, command=self._capture_one)
        self.btn_capture.pack(side="left", padx=3)

        self.btn_burst = ctk.CTkButton(ctrl_inner, text="Burst (10 shots)",
                                        fg_color="#4e6b8a", hover_color="#3d5670",
                                        width=130, command=self._burst_capture)
        self.btn_burst.pack(side="left", padx=3)

        # Auto-capture
        ctk.CTkLabel(ctrl_inner, text="Auto every:").pack(side="left", padx=(15, 3))
        self.interval_var = ctk.DoubleVar(value=2.0)
        ctk.CTkEntry(ctrl_inner, textvariable=self.interval_var,
                      width=50).pack(side="left", padx=(0, 3))
        ctk.CTkLabel(ctrl_inner, text="sec").pack(side="left")

        self.btn_auto = ctk.CTkButton(ctrl_inner, text="Start Auto",
                                       fg_color="#8a6b2d", hover_color="#705523",
                                       width=100, command=self._toggle_auto)
        self.btn_auto.pack(side="left", padx=(10, 3))

        # === Hotkey info ===
        info_frame = ctk.CTkFrame(self, corner_radius=8)
        info_frame.pack(fill="x", padx=10, pady=5)

        info_text = (
            "Hotkeys:  F5 = Capture single  |  F6 = Start/Stop auto-capture  |  F7 = Burst (10)  |  ESC = Quit\n\n"
            "Tips for good training data:\n"
            "  - Capture 2000-5000+ images across different maps, distances, angles\n"
            "  - Include close, medium, and far range enemies\n"
            "  - Capture different skins, lighting, smoke, flash situations\n"
            "  - Label 2 classes: 'enemy' (full body bbox) and 'head' (head bbox)\n"
            "  - Use tools like labelImg, CVAT, or Roboflow for labeling\n"
            "  - Train with: yolo detect train data=dataset.yaml model=yolov8s.pt epochs=100"
        )

        self.info_label = ctk.CTkLabel(info_frame, text=info_text,
                                        font=ctk.CTkFont(size=12),
                                        justify="left", anchor="w")
        self.info_label.pack(padx=10, pady=8, anchor="w")

        # === Status ===
        self.status_label = ctk.CTkLabel(self, text="Ready. Press F5 to capture.",
                                          font=ctk.CTkFont(size=12))
        self.status_label.pack(padx=10, pady=(0, 10))

        # Bind hotkeys
        self.bind_all("<F5>", lambda e: self._capture_one())
        self.bind_all("<F6>", lambda e: self._toggle_auto())
        self.bind_all("<F7>", lambda e: self._burst_capture())
        self.bind_all("<Escape>", lambda e: self._quit())

    def _populate_monitors(self):
        try:
            sct = mss.mss()
            monitors = sct.monitors
            values = []
            for i, m in enumerate(monitors):
                if i == 0:
                    values.append(f"0 - All ({m['width']}x{m['height']})")
                else:
                    values.append(f"{i} - Monitor {i} ({m['width']}x{m['height']})")
            sct.close()
            self.monitor_dropdown.configure(values=values)
            if len(values) > 1:
                self.monitor_var.set(values[1])
            else:
                self.monitor_var.set(values[0])
        except Exception:
            pass

    def _get_monitor_index(self) -> int:
        try:
            return int(self.monitor_var.get().split(" - ")[0])
        except Exception:
            return 1

    def _get_capture_region(self, sct) -> dict:
        """Get capture region based on mode selection."""
        mon_idx = self._get_monitor_index()
        monitor = sct.monitors[mon_idx]
        mode = self.capture_mode_var.get()

        if mode == "fullscreen":
            return monitor

        # Parse center NxN
        parts = mode.replace("center ", "").split("x")
        w, h = int(parts[0]), int(parts[1])

        cx = monitor["left"] + monitor["width"] // 2
        cy = monitor["top"] + monitor["height"] // 2

        return {
            "left": cx - w // 2,
            "top": cy - h // 2,
            "width": w,
            "height": h,
        }

    def _capture_one(self):
        """Capture a single screenshot."""
        output_dir = self.output_entry.get()
        os.makedirs(output_dir, exist_ok=True)

        try:
            sct = mss.mss()
            region = self._get_capture_region(sct)
            raw = sct.grab(region)
            frame = np.array(raw, dtype=np.uint8)[:, :, :3]  # BGRA -> BGR
            sct.close()

            # Generate filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            ext = self.format_var.get()
            filename = f"cs2_{timestamp}.{ext}"
            filepath = os.path.join(output_dir, filename)

            # Save
            if ext == "jpg":
                quality = int(self.quality_var.get())
                cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
            else:
                cv2.imwrite(filepath, frame)

            self._capture_count += 1
            self.count_label.configure(text=f"Captured: {self._capture_count}")
            self.status_label.configure(text=f"Saved: {filename}")

        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")

    def _burst_capture(self):
        """Capture 10 shots quickly in background."""
        def burst():
            for i in range(10):
                if self._stop_event.is_set():
                    break
                self.after(0, self._capture_one)
                time.sleep(0.3)
            self.after(0, lambda: self.status_label.configure(text="Burst complete!"))

        threading.Thread(target=burst, daemon=True).start()
        self.status_label.configure(text="Burst capturing (10 shots)...")

    def _toggle_auto(self):
        """Toggle auto-capture."""
        if self._auto_running:
            self._auto_running = False
            self._stop_event.set()
            self.btn_auto.configure(text="Start Auto", fg_color="#8a6b2d")
            self.status_label.configure(text="Auto-capture stopped.")
        else:
            self._auto_running = True
            self._stop_event.clear()
            self.btn_auto.configure(text="Stop Auto", fg_color="#8a2d2d")
            self.status_label.configure(text="Auto-capture running...")

            def auto_loop():
                while self._auto_running and not self._stop_event.is_set():
                    self.after(0, self._capture_one)
                    try:
                        interval = float(self.interval_var.get())
                    except Exception:
                        interval = 2.0
                    time.sleep(max(0.2, interval))

            threading.Thread(target=auto_loop, daemon=True).start()

    def _start_live_preview(self):
        """Start background thread that continuously captures for preview."""
        def preview_loop():
            while not self._stop_event.is_set():
                try:
                    sct = mss.mss()
                    region = self._get_capture_region(sct)
                    raw = sct.grab(region)
                    frame = np.array(raw, dtype=np.uint8)[:, :, :3]
                    sct.close()

                    # Resize for preview
                    h, w = frame.shape[:2]
                    scale = min(self.PREVIEW_W / w, self.PREVIEW_H / h)
                    new_w, new_h = int(w * scale), int(h * scale)
                    resized = cv2.resize(frame, (new_w, new_h))

                    # Convert BGR -> RGB
                    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

                    # Add info text
                    cv2.putText(rgb, f"Resolution: {w}x{h}", (8, 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                    pil_img = Image.fromarray(rgb)

                    with self._lock:
                        self._preview_image = pil_img

                except Exception:
                    pass
                time.sleep(0.05)  # ~20 fps preview

        self._preview_thread = threading.Thread(target=preview_loop, daemon=True)
        self._preview_thread.start()

    def _update_preview_loop(self):
        """Update preview in main thread."""
        with self._lock:
            img = self._preview_image

        if img is not None:
            tk_img = ImageTk.PhotoImage(img)
            self.preview_label.configure(image=tk_img, text="")
            self.preview_label._tk_img = tk_img

        self.after(50, self._update_preview_loop)

    def _browse_output(self):
        from tkinter import filedialog
        path = filedialog.askdirectory(title="Select Output Folder")
        if path:
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, path)

    def _quit(self):
        self._stop_event.set()
        self._auto_running = False
        self.destroy()


def main():
    app = CaptureToolGUI()
    app.protocol("WM_DELETE_WINDOW", app._quit)
    app.mainloop()


if __name__ == "__main__":
    main()
