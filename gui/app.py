"""
CS2 AI Aimbot - Desktop GUI Application
Full control panel with live preview, monitor selection, and all settings.
"""
import customtkinter as ctk
import threading
import time
import cv2
import numpy as np
from PIL import Image, ImageTk
from typing import Optional
import mss


class AimbotGUI(ctk.CTk):
    """Main application window."""

    PREVIEW_WIDTH = 480
    PREVIEW_HEIGHT = 480

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.game_overlay = None

        # State
        self._running = False
        self._bot_thread: Optional[threading.Thread] = None
        self._preview_image = None
        self._fps = 0.0
        self._inference_ms = 0.0
        self._lock = threading.Lock()
        self._stop_event = threading.Event()

        self.on_start = None
        self.on_stop = None

        self._setup_window()
        self._build_ui()
        self._populate_monitors()
        self._init_overlay()
        self._update_preview_loop()

    def _setup_window(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.title("CS2 AI Aimbot")
        self.geometry("560x920")
        self.minsize(520, 750)
        self.resizable(True, True)
        self.attributes("-topmost", False)

    def _build_ui(self):
        # === Preview ===
        self.preview_frame = ctk.CTkFrame(self, corner_radius=8)
        self.preview_frame.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(self.preview_frame, text="Live Preview",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(
            anchor="w", padx=10, pady=(5, 0))

        self.preview_canvas = ctk.CTkLabel(self.preview_frame, text="No feed",
                                           width=self.PREVIEW_WIDTH,
                                           height=self.PREVIEW_HEIGHT)
        self.preview_canvas.pack(padx=10, pady=10)

        # === Status bar ===
        status_frame = ctk.CTkFrame(self, corner_radius=8)
        status_frame.pack(fill="x", padx=10, pady=5)
        status_inner = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_inner.pack(fill="x", padx=10, pady=8)

        self.status_label = ctk.CTkLabel(status_inner, text="Status: Stopped",
                                         font=ctk.CTkFont(size=13, weight="bold"),
                                         text_color="#ff5555")
        self.status_label.pack(side="left")
        self.fps_label = ctk.CTkLabel(status_inner, text="FPS: --  |  Inference: --ms",
                                      font=ctk.CTkFont(size=12))
        self.fps_label.pack(side="right")

        # === Monitor + Team + Controls ===
        ctrl_frame = ctk.CTkFrame(self, corner_radius=8)
        ctrl_frame.pack(fill="x", padx=10, pady=5)

        row1 = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=(8, 3))

        ctk.CTkLabel(row1, text="Monitor:").pack(side="left", padx=(0, 5))
        self.monitor_var = ctk.StringVar(value="1")
        self.monitor_dropdown = ctk.CTkOptionMenu(row1, variable=self.monitor_var,
                                                   values=["1"], width=170,
                                                   command=self._on_monitor_change)
        self.monitor_dropdown.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(row1, text="Team:").pack(side="left", padx=(0, 5))
        self.team_var = ctk.StringVar(value=self.config["my_team"])
        ctk.CTkOptionMenu(row1, variable=self.team_var,
                           values=["ct", "t"], width=70,
                           command=lambda v: self._set("my_team", v)
                           ).pack(side="left")

        row2 = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=(3, 8))

        self.btn_start = ctk.CTkButton(row2, text="Start",
                                        fg_color="#2d8a4e", hover_color="#23713f",
                                        width=80, command=self._on_start)
        self.btn_start.pack(side="left", padx=3)
        self.btn_stop = ctk.CTkButton(row2, text="Stop",
                                       fg_color="#8a2d2d", hover_color="#712323",
                                       width=80, command=self._on_stop, state="disabled")
        self.btn_stop.pack(side="left", padx=3)

        self.overlay_toggle_var = ctk.BooleanVar(value=self.config["overlay_enabled"])
        ctk.CTkSwitch(row2, text="Game Overlay",
                       variable=self.overlay_toggle_var,
                       command=self._toggle_overlay).pack(side="left", padx=(15, 0))

        # === Tabs ===
        self.tabview = ctk.CTkTabview(self, corner_radius=8)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=(5, 5))

        self._build_tab_aimbot()
        self._build_tab_target()
        self._build_tab_triggerbot()
        self._build_tab_visuals()
        self._build_tab_performance()

        # === Bottom ===
        bottom_frame = ctk.CTkFrame(self, corner_radius=8)
        bottom_frame.pack(fill="x", padx=10, pady=(0, 10))
        bottom_inner = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        bottom_inner.pack(fill="x", padx=10, pady=8)

        ctk.CTkButton(bottom_inner, text="Save Config", width=110,
                       command=self._save_config).pack(side="left", padx=3)
        ctk.CTkButton(bottom_inner, text="Load Config", width=110,
                       command=self._load_config).pack(side="left", padx=3)
        ctk.CTkButton(bottom_inner, text="Reset", width=80,
                       fg_color="#6b4c00", hover_color="#554000",
                       command=self._reset_config).pack(side="left", padx=3)

        self.topmost_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(bottom_inner, text="Pin", variable=self.topmost_var,
                        command=self._toggle_topmost).pack(side="right", padx=3)

    # ──────────────────────── Aimbot Tab ────────────────────────

    def _build_tab_aimbot(self):
        tab = self.tabview.add("Aimbot")

        self.aim_enabled_var = ctk.BooleanVar(value=self.config["enabled"])
        ctk.CTkSwitch(tab, text="Aimbot Enabled", variable=self.aim_enabled_var,
                       command=lambda: self._set("enabled", self.aim_enabled_var.get()),
                       ).pack(anchor="w", padx=15, pady=(10, 5))

        mode_frame = ctk.CTkFrame(tab, fg_color="transparent")
        mode_frame.pack(fill="x", padx=15, pady=3)
        ctk.CTkLabel(mode_frame, text="Aim Mode:").pack(side="left")
        self.aim_mode_var = ctk.StringVar(value=self.config["aim_mode"])
        ctk.CTkOptionMenu(mode_frame, variable=self.aim_mode_var,
                           values=["trigger", "hold", "always"], width=140,
                           command=lambda v: self._set("aim_mode", v)).pack(side="right")

        self.fov_var = ctk.IntVar(value=self.config["fov_radius"])
        self._add_slider(tab, "FOV Radius", self.fov_var, 20, 500,
                         lambda v: self._set("fov_radius", int(v)))

        self.smooth_var = ctk.DoubleVar(value=self.config["smoothing"])
        self._add_slider(tab, "Smoothing", self.smooth_var, 0.0, 0.95,
                         lambda v: self._set("smoothing", round(float(v), 3)),
                         resolution=0.01)

        self.humanize_var = ctk.BooleanVar(value=self.config["humanize"])
        ctk.CTkSwitch(tab, text="Humanize", variable=self.humanize_var,
                       command=lambda: self._set("humanize", self.humanize_var.get()),
                       ).pack(anchor="w", padx=15, pady=3)

        self.jitter_var = ctk.DoubleVar(value=self.config["humanize_jitter"])
        self._add_slider(tab, "Jitter", self.jitter_var, 0.0, 10.0,
                         lambda v: self._set("humanize_jitter", round(float(v), 2)),
                         resolution=0.1)

        self.speed_var = ctk.IntVar(value=self.config["max_move_per_tick"])
        self._add_slider(tab, "Max Speed", self.speed_var, 10, 200,
                         lambda v: self._set("max_move_per_tick", int(v)))

    # ──────────────────────── Target Tab ────────────────────────

    def _build_tab_target(self):
        tab = self.tabview.add("Target")

        self.prefer_head_var = ctk.BooleanVar(value=self.config.get("prefer_head", True))
        ctk.CTkSwitch(tab, text="Prefer Head (aim at head bbox center)",
                       variable=self.prefer_head_var,
                       command=lambda: self._set("prefer_head", self.prefer_head_var.get()),
                       ).pack(anchor="w", padx=15, pady=(10, 5))

        bone_frame = ctk.CTkFrame(tab, fg_color="transparent")
        bone_frame.pack(fill="x", padx=15, pady=3)
        ctk.CTkLabel(bone_frame, text="Body Bone (fallback):").pack(side="left")
        self.bone_var = ctk.StringVar(value=self.config["target_bone"])
        ctk.CTkOptionMenu(bone_frame, variable=self.bone_var,
                           values=["head", "neck", "chest", "body"], width=140,
                           command=lambda v: self._set("target_bone", v)).pack(side="right")

        sort_frame = ctk.CTkFrame(tab, fg_color="transparent")
        sort_frame.pack(fill="x", padx=15, pady=3)
        ctk.CTkLabel(sort_frame, text="Sort By:").pack(side="left")
        self.sort_var = ctk.StringVar(value=self.config["target_sort"])
        ctk.CTkOptionMenu(sort_frame, variable=self.sort_var,
                           values=["distance", "confidence", "area"], width=140,
                           command=lambda v: self._set("target_sort", v)).pack(side="right")

        self.conf_var = ctk.DoubleVar(value=self.config["confidence_threshold"])
        self._add_slider(tab, "Confidence", self.conf_var, 0.1, 0.95,
                         lambda v: self._set("confidence_threshold", round(float(v), 2)),
                         resolution=0.01)

        self.head_r_var = ctk.DoubleVar(value=self.config["head_ratio"])
        self._add_slider(tab, "Head Pos (body fallback)", self.head_r_var, 0.05, 0.5,
                         lambda v: self._set("head_ratio", round(float(v), 2)),
                         resolution=0.01)

        self.region_w_var = ctk.IntVar(value=self.config["detection_region_width"])
        self._add_slider(tab, "Capture Width", self.region_w_var, 320, 1280,
                         lambda v: self._set("detection_region_width", int(v)))

        self.region_h_var = ctk.IntVar(value=self.config["detection_region_height"])
        self._add_slider(tab, "Capture Height", self.region_h_var, 320, 1280,
                         lambda v: self._set("detection_region_height", int(v)))

    # ──────────────────────── Triggerbot Tab ────────────────────────

    def _build_tab_triggerbot(self):
        tab = self.tabview.add("Trigger")

        self.trig_var = ctk.BooleanVar(value=self.config["triggerbot_enabled"])
        ctk.CTkSwitch(tab, text="Triggerbot Enabled", variable=self.trig_var,
                       command=lambda: self._set("triggerbot_enabled", self.trig_var.get()),
                       ).pack(anchor="w", padx=15, pady=(10, 5))

        self.trig_min_var = ctk.IntVar(value=self.config["triggerbot_delay_min"])
        self._add_slider(tab, "Min Delay (ms)", self.trig_min_var, 0, 500,
                         lambda v: self._set("triggerbot_delay_min", int(v)))

        self.trig_max_var = ctk.IntVar(value=self.config["triggerbot_delay_max"])
        self._add_slider(tab, "Max Delay (ms)", self.trig_max_var, 0, 500,
                         lambda v: self._set("triggerbot_delay_max", int(v)))

        ctk.CTkLabel(tab, text="─── Recoil Control ───",
                     font=ctk.CTkFont(size=12)).pack(padx=15, pady=(15, 5))

        self.rcs_var = ctk.BooleanVar(value=self.config["rcs_enabled"])
        ctk.CTkSwitch(tab, text="RCS Enabled", variable=self.rcs_var,
                       command=lambda: self._set("rcs_enabled", self.rcs_var.get()),
                       ).pack(anchor="w", padx=15, pady=3)

        self.rcs_x_var = ctk.DoubleVar(value=self.config["rcs_strength_x"])
        self._add_slider(tab, "RCS X", self.rcs_x_var, 0.0, 1.0,
                         lambda v: self._set("rcs_strength_x", round(float(v), 2)),
                         resolution=0.05)

        self.rcs_y_var = ctk.DoubleVar(value=self.config["rcs_strength_y"])
        self._add_slider(tab, "RCS Y", self.rcs_y_var, 0.0, 1.0,
                         lambda v: self._set("rcs_strength_y", round(float(v), 2)),
                         resolution=0.05)

    # ──────────────────────── Visuals Tab ────────────────────────

    def _build_tab_visuals(self):
        tab = self.tabview.add("Visuals")

        toggles = [
            ("FOV Circle", "show_fov_circle"),
            ("Bounding Boxes", "show_bounding_boxes"),
            ("Snaplines", "show_snaplines"),
            ("Crosshair", "show_crosshair"),
            ("Show FPS", "show_fps"),
            ("Target Info", "show_target_info"),
        ]

        self._visual_vars = {}
        for label, key in toggles:
            var = ctk.BooleanVar(value=self.config[key])
            self._visual_vars[key] = var
            ctk.CTkSwitch(tab, text=label, variable=var,
                           command=lambda k=key, v=var: self._set(k, v.get()),
                           ).pack(anchor="w", padx=15, pady=2)

    # ──────────────────────── Performance Tab ────────────────────────

    def _build_tab_performance(self):
        tab = self.tabview.add("Perf")

        dev_frame = ctk.CTkFrame(tab, fg_color="transparent")
        dev_frame.pack(fill="x", padx=15, pady=(10, 3))
        ctk.CTkLabel(dev_frame, text="Device:").pack(side="left")
        self.device_var = ctk.StringVar(value=self.config["device"])
        ctk.CTkOptionMenu(dev_frame, variable=self.device_var,
                           values=["cuda", "cpu"], width=140,
                           command=lambda v: self._set("device", v)).pack(side="right")

        imgsz_frame = ctk.CTkFrame(tab, fg_color="transparent")
        imgsz_frame.pack(fill="x", padx=15, pady=3)
        ctk.CTkLabel(imgsz_frame, text="YOLO ImgSz:").pack(side="left")
        self.imgsz_var = ctk.StringVar(value=str(self.config["imgsz"]))
        ctk.CTkOptionMenu(imgsz_frame, variable=self.imgsz_var,
                           values=["320", "416", "512", "640", "768", "1024"],
                           width=140,
                           command=lambda v: self._set("imgsz", int(v))).pack(side="right")

        self.half_var = ctk.BooleanVar(value=self.config["half_precision"])
        ctk.CTkSwitch(tab, text="FP16 (Half Precision)", variable=self.half_var,
                       command=lambda: self._set("half_precision", self.half_var.get()),
                       ).pack(anchor="w", padx=15, pady=3)

        self.fps_limit_var = ctk.IntVar(value=self.config["fps_limit"])
        self._add_slider(tab, "FPS Limit (0=off)", self.fps_limit_var, 0, 300,
                         lambda v: self._set("fps_limit", int(v)))

        ctk.CTkLabel(tab, text="─── Model ───",
                     font=ctk.CTkFont(size=12)).pack(padx=15, pady=(15, 5))

        model_frame = ctk.CTkFrame(tab, fg_color="transparent")
        model_frame.pack(fill="x", padx=15, pady=3)
        self.model_entry = ctk.CTkEntry(model_frame, width=280)
        self.model_entry.insert(0, self.config["model_path"])
        self.model_entry.pack(side="left", padx=(0, 5))
        ctk.CTkButton(model_frame, text="Browse", width=70,
                       command=self._browse_model).pack(side="left")

    # ──────────────────────── Helpers ────────────────────────

    def _add_slider(self, parent, label, variable, from_, to, command, resolution=1):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=15, pady=3)
        ctk.CTkLabel(frame, text=f"{label}:", width=150, anchor="w").pack(side="left")
        val_label = ctk.CTkLabel(frame, text=str(variable.get()), width=50, anchor="e")
        val_label.pack(side="right")

        def on_change(v):
            if isinstance(variable, ctk.IntVar):
                variable.set(int(float(v)))
                val_label.configure(text=str(int(float(v))))
            else:
                variable.set(round(float(v), 3))
                val_label.configure(text=f"{float(v):.2f}")
            command(v)

        slider = ctk.CTkSlider(frame, from_=from_, to=to, variable=variable,
                                command=on_change, width=200)
        if resolution != 1:
            slider.configure(number_of_steps=int((to - from_) / resolution))
        slider.pack(side="right", padx=(5, 5))

    def _set(self, key, value):
        self.config[key] = value

    # ──────────────────────── Overlay ────────────────────────

    def _init_overlay(self):
        """Prepare overlay (lazy - only created when enabled)."""
        self.game_overlay = None
        if self.config["overlay_enabled"]:
            self._create_overlay()

    def _create_overlay(self):
        """Actually create the transparent game overlay window."""
        try:
            from core.game_overlay import GameOverlay
            self.game_overlay = GameOverlay(self, self.config)
            self.game_overlay.create()
            # If creation failed (e.g. no click-through support), overlay is None-like
            if self.game_overlay.window is None:
                print("[!] Overlay creation failed - disabled")
                self.game_overlay = None
                self.config["overlay_enabled"] = False
                self.overlay_toggle_var.set(False)
        except Exception as e:
            print(f"[!] Game overlay init failed: {e}")
            self.game_overlay = None
            self.config["overlay_enabled"] = False
            self.overlay_toggle_var.set(False)

    def _toggle_overlay(self):
        val = self.overlay_toggle_var.get()
        self.config["overlay_enabled"] = val
        if val:
            if self.game_overlay is None:
                self._create_overlay()
            elif self.game_overlay:
                self.game_overlay.show()
        else:
            if self.game_overlay:
                self.game_overlay.hide()

    # ──────────────────────── Monitors ────────────────────────

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
            idx = self.config.get("monitor_index", 1)
            if idx < len(values):
                self.monitor_var.set(values[idx])
            else:
                self.monitor_var.set(values[1] if len(values) > 1 else values[0])
        except Exception:
            pass

    def _on_monitor_change(self, value):
        try:
            idx = int(value.split(" - ")[0])
            self.config["monitor_index"] = idx
        except Exception:
            pass

    # ──────────────────────── Start/Stop ────────────────────────

    def _on_start(self):
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self._stop_event.clear()
        self._running = True
        self._update_status("Running", "#55ff55")
        if self.on_start:
            self._bot_thread = threading.Thread(target=self.on_start,
                                                 args=(self._stop_event,), daemon=True)
            self._bot_thread.start()

    def _on_stop(self):
        self._stop_event.set()
        self._running = False
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self._update_status("Stopped", "#ff5555")
        if self.game_overlay and self.game_overlay.canvas:
            self.game_overlay.canvas.delete("all")
        if self.on_stop:
            self.on_stop()

    def _update_status(self, text, color):
        self.status_label.configure(text=f"Status: {text}", text_color=color)

    def _save_config(self):
        self.config["model_path"] = self.model_entry.get()
        self.config.save()
        self._flash_status("Config saved!", "#55aaff")

    def _load_config(self):
        self.config.load()
        self._refresh_ui_from_config()
        self._flash_status("Config loaded!", "#55aaff")

    def _reset_config(self):
        self.config.reset()
        self._refresh_ui_from_config()
        self._flash_status("Reset to defaults!", "#ffaa55")

    def _flash_status(self, text, color):
        old_text = self.status_label.cget("text")
        old_color = self.status_label.cget("text_color")
        self.status_label.configure(text=text, text_color=color)
        self.after(2000, lambda: self.status_label.configure(
            text=old_text, text_color=old_color))

    def _refresh_ui_from_config(self):
        cfg = self.config
        self.aim_enabled_var.set(cfg["enabled"])
        self.aim_mode_var.set(cfg["aim_mode"])
        self.fov_var.set(cfg["fov_radius"])
        self.smooth_var.set(cfg["smoothing"])
        self.humanize_var.set(cfg["humanize"])
        self.jitter_var.set(cfg["humanize_jitter"])
        self.speed_var.set(cfg["max_move_per_tick"])
        self.prefer_head_var.set(cfg.get("prefer_head", True))
        self.bone_var.set(cfg["target_bone"])
        self.sort_var.set(cfg["target_sort"])
        self.conf_var.set(cfg["confidence_threshold"])
        self.head_r_var.set(cfg["head_ratio"])
        self.region_w_var.set(cfg["detection_region_width"])
        self.region_h_var.set(cfg["detection_region_height"])
        self.trig_var.set(cfg["triggerbot_enabled"])
        self.trig_min_var.set(cfg["triggerbot_delay_min"])
        self.trig_max_var.set(cfg["triggerbot_delay_max"])
        self.rcs_var.set(cfg["rcs_enabled"])
        self.rcs_x_var.set(cfg["rcs_strength_x"])
        self.rcs_y_var.set(cfg["rcs_strength_y"])
        self.overlay_toggle_var.set(cfg["overlay_enabled"])
        self.team_var.set(cfg["my_team"])
        for key, var in self._visual_vars.items():
            var.set(cfg[key])
        self.device_var.set(cfg["device"])
        self.imgsz_var.set(str(cfg["imgsz"]))
        self.half_var.set(cfg["half_precision"])
        self.fps_limit_var.set(cfg["fps_limit"])
        self.model_entry.delete(0, "end")
        self.model_entry.insert(0, cfg["model_path"])

    def _browse_model(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Select YOLO Model",
            filetypes=[("PyTorch Model", "*.pt"), ("All Files", "*.*")])
        if path:
            self.model_entry.delete(0, "end")
            self.model_entry.insert(0, path)
            self.config["model_path"] = path

    def _toggle_topmost(self):
        self.attributes("-topmost", self.topmost_var.get())

    # ──────────────────────── Preview ────────────────────────

    def update_preview(self, frame: np.ndarray, detections: list,
                       fps: float, inference_ms: float,
                       capture_offset: tuple, screen_center: tuple,
                       target=None):
        """Called from bot thread to update the preview image."""
        display = frame.copy()
        cfg = self.config
        h, w = display.shape[:2]
        local_cx, local_cy = w // 2, h // 2
        head_ids = set(cfg.get("head_class_ids", [1, 3]))

        if cfg["show_fov_circle"]:
            cv2.circle(display, (local_cx, local_cy),
                       int(cfg["fov_radius"]), (255, 255, 255), 1)

        if cfg["show_bounding_boxes"]:
            for det in detections:
                x1, y1, x2, y2 = int(det.x1), int(det.y1), int(det.x2), int(det.y2)
                is_head = det.class_id in head_ids
                color = (255, 0, 255) if is_head else (50, 50, 255)

                corner = max(8, min(x2 - x1, y2 - y1) // 4)
                th = 2
                cv2.line(display, (x1, y1), (x1 + corner, y1), color, th)
                cv2.line(display, (x1, y1), (x1, y1 + corner), color, th)
                cv2.line(display, (x2, y1), (x2 - corner, y1), color, th)
                cv2.line(display, (x2, y1), (x2, y1 + corner), color, th)
                cv2.line(display, (x1, y2), (x1 + corner, y2), color, th)
                cv2.line(display, (x1, y2), (x1, y2 - corner), color, th)
                cv2.line(display, (x2, y2), (x2 - corner, y2), color, th)
                cv2.line(display, (x2, y2), (x2, y2 - corner), color, th)

                label = f"{det.confidence:.0%} {det.class_name}"
                cv2.putText(display, label, (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)

                if is_head:
                    cx, cy = int(det.center[0]), int(det.center[1])
                    cv2.circle(display, (cx, cy), 3, (0, 255, 0), -1)
                else:
                    aim_pt = det.get_aim_point(bone=cfg["target_bone"],
                                                head_r=cfg["head_ratio"])
                    cv2.circle(display, (int(aim_pt[0]), int(aim_pt[1])),
                               3, (0, 255, 0), -1)

        if target is not None and hasattr(target, "aim_point"):
            tx, ty = int(target.aim_point[0]), int(target.aim_point[1])
            cv2.circle(display, (tx, ty), 6, (0, 0, 255), 2)
            cv2.drawMarker(display, (tx, ty), (0, 255, 255),
                           cv2.MARKER_CROSS, 10, 1)

        cv2.drawMarker(display, (local_cx, local_cy), (0, 255, 0),
                        cv2.MARKER_CROSS, 12, 1)

        info_lines = [
            f"FPS: {fps:.0f}  |  Inference: {inference_ms:.1f}ms",
            f"Targets: {len(detections)}  |  Team: {cfg['my_team'].upper()}",
        ]
        for i, line in enumerate(info_lines):
            cv2.putText(display, line, (8, 18 + i * 18),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

        display_rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(display_rgb)
        pil_img = pil_img.resize((self.PREVIEW_WIDTH, self.PREVIEW_HEIGHT),
                                  Image.BILINEAR)

        with self._lock:
            self._preview_image = pil_img
            self._fps = fps
            self._inference_ms = inference_ms

    def _update_preview_loop(self):
        with self._lock:
            img = self._preview_image
            fps = self._fps
            ms = self._inference_ms

        if img is not None:
            tk_img = ImageTk.PhotoImage(img)
            self.preview_canvas.configure(image=tk_img, text="")
            self.preview_canvas._tk_img = tk_img
            self.fps_label.configure(text=f"FPS: {fps:.0f}  |  Inference: {ms:.1f}ms")

        self.after(33, self._update_preview_loop)

    def on_close(self):
        self._stop_event.set()
        self._running = False
        if self.game_overlay:
            self.game_overlay.destroy()
        self.config.save()
        self.destroy()
