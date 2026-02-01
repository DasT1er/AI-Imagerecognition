"""
CS2 AI Aimbot - Configuration
All settings in one place. Editable at runtime via GUI.
"""
import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

DEFAULT_CONFIG = {
    # --- General ---
    "enabled": False,
    "toggle_key": "F1",
    "panic_key": "F12",           # Kill switch - disables everything instantly
    "menu_key": "INSERT",

    # --- Detection ---
    "model_path": "models/best.pt",
    "confidence_threshold": 0.45,
    "device": "cuda",              # "cuda" or "cpu"
    "imgsz": 640,
    "detection_region_width": 640,
    "detection_region_height": 640,

    # --- Target Selection ---
    "target_classes": [0],         # YOLO class IDs to target (0 = enemy typically)
    "target_bone": "head",         # "head", "neck", "chest", "body"
    "head_ratio": 0.15,            # How far from top of bbox to aim for head
    "neck_ratio": 0.25,
    "chest_ratio": 0.35,
    "body_ratio": 0.50,
    "target_sort": "distance",     # "distance" (to crosshair), "confidence", "area"

    # --- Aim ---
    "aim_mode": "trigger",         # "trigger" = only when shooting, "hold" = hold key, "always"
    "aim_key": None,               # None = mouse1 trigger, or specific key like "XBUTTON2"
    "fov_radius": 150,             # Pixel radius from crosshair - ignore targets outside
    "smoothing": 0.45,             # 0.0 = instant snap, 1.0 = very slow (lower = faster)
    "smoothing_curve": "bezier",   # "linear", "bezier", "ease_out", "ease_in_out"
    "humanize": True,
    "humanize_jitter": 2.5,        # Random pixel offset to look human
    "humanize_delay_min": 0.0,     # Min random delay before moving (ms)
    "humanize_delay_max": 5.0,     # Max random delay before moving (ms)
    "max_move_per_tick": 80,       # Max pixels to move per frame (speed cap)
    "flick_enabled": True,         # Allow fast flicks for close targets
    "flick_threshold": 30,         # Below this distance -> flick
    "prediction_enabled": True,    # Lead targets based on velocity
    "prediction_factor": 0.3,      # How much to lead

    # --- Recoil Control (RCS) ---
    "rcs_enabled": False,
    "rcs_strength_x": 0.5,        # Horizontal recoil compensation (0-1)
    "rcs_strength_y": 0.5,        # Vertical recoil compensation (0-1)

    # --- Triggerbot ---
    "triggerbot_enabled": False,
    "triggerbot_key": "XBUTTON1",  # Mouse side button
    "triggerbot_delay_min": 50,    # Min reaction time (ms)
    "triggerbot_delay_max": 150,   # Max reaction time (ms)

    # --- Visuals / Overlay ---
    "overlay_enabled": True,
    "show_fov_circle": True,
    "show_bounding_boxes": True,
    "show_snaplines": False,
    "show_crosshair": True,
    "show_fps": True,
    "show_target_info": True,
    "box_color": [255, 50, 50],
    "fov_color": [255, 255, 255],
    "crosshair_color": [0, 255, 0],
    "snapline_color": [255, 255, 0],
    "overlay_opacity": 0.85,

    # --- Performance ---
    "fps_limit": 0,               # 0 = unlimited
    "half_precision": True,        # FP16 inference (faster on RTX GPUs)
    "verbose": False,
}


class Config:
    """Runtime configuration with save/load support."""

    def __init__(self):
        self._data = dict(DEFAULT_CONFIG)
        self.load()

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def get(self, key, default=None):
        return self._data.get(key, default)

    def update(self, d: dict):
        self._data.update(d)

    def items(self):
        return self._data.items()

    def save(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self._data, f, indent=2)
        except Exception:
            pass

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    saved = json.load(f)
                self._data.update(saved)
            except Exception:
                pass

    def reset(self):
        self._data = dict(DEFAULT_CONFIG)
        self.save()

    def to_dict(self):
        return dict(self._data)
