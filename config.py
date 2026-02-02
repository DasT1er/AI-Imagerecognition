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
    "monitor_index": 1,

    # --- Detection ---
    "model_path": "models/best.pt",
    "confidence_threshold": 0.45,
    "device": "cuda",              # "cuda" or "cpu"
    "imgsz": 640,
    "detection_region_width": 640,
    "detection_region_height": 640,

    # --- Target Selection ---
    # 4-class model: 0=t, 1=t_head, 2=ct, 3=ct_head
    # Set which team you are on - bot will target the OTHER team
    "my_team": "ct",               # "ct" or "t" - your team (targets enemy team)
    "target_classes": [0, 1],      # Auto-set: ct targets [0,1] (t+t_head), t targets [2,3]
    "head_class_ids": [1, 3],      # Which class IDs are head detections
    "body_class_ids": [0, 2],      # Which class IDs are body detections
    "prefer_head": True,           # If head detected, aim at head bbox center instead of body ratio
    "target_bone": "head",         # Fallback for body bbox: "head", "neck", "chest", "body"
    "head_ratio": 0.15,            # How far from top of body bbox for head estimate
    "neck_ratio": 0.25,
    "chest_ratio": 0.35,
    "body_ratio": 0.50,
    "target_sort": "distance",     # "distance" (to crosshair), "confidence", "area"

    # --- Aim ---
    "aim_mode": "trigger",         # "trigger" = only when shooting, "hold" = hold key, "always"
    "aim_key": None,               # None = mouse1 trigger, or specific key like "XBUTTON2"
    "fov_radius": 150,             # Pixel radius from crosshair - ignore targets outside
    "smoothing": 0.35,             # 0.0 = instant snap, 1.0 = very slow (lower = faster)
    "smoothing_curve": "bezier",   # "linear", "bezier", "ease_out", "ease_in_out"
    "distance_scaling": True,      # Move faster when far, slower when close
    "humanize": True,
    "humanize_jitter": 1.5,        # Random pixel offset to look human
    "humanize_delay_min": 0.0,     # Min random delay before moving (ms)
    "humanize_delay_max": 3.0,     # Max random delay before moving (ms)
    "max_move_per_tick": 120,      # Max pixels to move per frame (speed cap)
    "min_move_threshold": 0.5,     # Don't move if delta < this (avoids twitching)
    "flick_enabled": True,         # Allow fast flicks for close targets
    "flick_threshold": 25,         # Below this distance -> flick
    "prediction_enabled": True,    # Lead targets based on velocity
    "prediction_factor": 0.25,     # How much to lead

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
    "overlay_enabled": False,
    "show_fov_circle": True,
    "show_bounding_boxes": True,
    "show_snaplines": False,
    "show_crosshair": True,
    "show_fps": True,
    "show_target_info": True,
    "box_color": [255, 50, 50],
    "head_box_color": [255, 0, 255],
    "fov_color": [255, 255, 255],
    "crosshair_color": [0, 255, 0],
    "snapline_color": [255, 255, 0],

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

    def setup_classes_from_model(self, class_names: dict):
        """
        Auto-detect head/body/team class IDs from model class names.
        Supports any model: 2-class (player/head), 4-class (t/t_head/ct/ct_head), etc.
        """
        self._data["_model_class_names"] = class_names
        num = len(class_names)

        # Detect head classes by name (contains "head")
        head_ids = []
        body_ids = []
        t_ids = []
        ct_ids = []

        for cid, name in class_names.items():
            name_lower = name.lower()
            is_head = "head" in name_lower
            is_t = name_lower.startswith("t") and not name_lower.startswith("ct")
            is_ct = name_lower.startswith("ct")

            if is_head:
                head_ids.append(int(cid))
            else:
                body_ids.append(int(cid))

            if is_t:
                t_ids.append(int(cid))
            elif is_ct:
                ct_ids.append(int(cid))

        self._data["head_class_ids"] = head_ids
        self._data["body_class_ids"] = body_ids
        self._data["_t_class_ids"] = t_ids      # All terrorist classes (body+head)
        self._data["_ct_class_ids"] = ct_ids     # All CT classes (body+head)
        self._data["_has_teams"] = len(t_ids) > 0 and len(ct_ids) > 0

        print(f"[+] Model classes: {class_names}")
        print(f"    Head IDs: {head_ids}, Body IDs: {body_ids}")
        print(f"    T IDs: {t_ids}, CT IDs: {ct_ids}")
        print(f"    Team-based model: {self._data['_has_teams']}")

        self.update_target_classes()

    def update_target_classes(self):
        """Set target_classes based on my_team selection and detected model classes."""
        has_teams = self._data.get("_has_teams", False)

        if has_teams:
            # 4-class model: filter by enemy team
            if self._data["my_team"] == "ct":
                self._data["target_classes"] = list(self._data["_t_class_ids"])
            else:
                self._data["target_classes"] = list(self._data["_ct_class_ids"])
        else:
            # 2-class or generic model: target ALL classes (no team filtering)
            names = self._data.get("_model_class_names", {})
            self._data["target_classes"] = [int(cid) for cid in names.keys()]

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
