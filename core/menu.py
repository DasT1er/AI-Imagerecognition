"""
In-game settings menu rendered on the overlay.
Toggle with INSERT key. Allows changing all settings at runtime.
"""
import pygame
from typing import Optional


class Menu:
    """Interactive settings menu rendered over the game."""

    BACKGROUND = (15, 15, 20, 230)
    HEADER_COLOR = (180, 60, 60)
    TEXT_COLOR = (220, 220, 220)
    VALUE_COLOR = (100, 255, 100)
    SELECTED_COLOR = (255, 255, 100)
    SEPARATOR_COLOR = (60, 60, 70)

    MENU_WIDTH = 380
    ITEM_HEIGHT = 24
    PADDING = 12

    def __init__(self, config):
        self.config = config
        self.visible = False
        self.selected_index = 0
        self.font = None
        self.font_header = None
        self._initialized = False

        # Menu structure: (label, config_key, type, min, max, step)
        self.items = [
            ("--- AIMBOT ---", None, "header", 0, 0, 0),
            ("Enabled", "enabled", "bool", 0, 0, 0),
            ("Aim Mode", "aim_mode", "choice", ["trigger", "hold", "always"], 0, 0),
            ("Target Bone", "target_bone", "choice", ["head", "neck", "chest", "body"], 0, 0),
            ("FOV Radius", "fov_radius", "int", 20, 500, 10),
            ("Smoothing", "smoothing", "float", 0.0, 0.95, 0.05),
            ("Smooth Curve", "smoothing_curve", "choice", ["bezier", "linear", "ease_out", "ease_in_out"], 0, 0),
            ("Humanize", "humanize", "bool", 0, 0, 0),
            ("Jitter", "humanize_jitter", "float", 0.0, 10.0, 0.5),
            ("Max Speed", "max_move_per_tick", "int", 10, 200, 5),
            ("Prediction", "prediction_enabled", "bool", 0, 0, 0),
            ("Pred. Factor", "prediction_factor", "float", 0.0, 1.0, 0.05),
            ("Flick Aim", "flick_enabled", "bool", 0, 0, 0),
            ("", None, "separator", 0, 0, 0),
            ("--- TARGET ---", None, "header", 0, 0, 0),
            ("Sort By", "target_sort", "choice", ["distance", "confidence", "area"], 0, 0),
            ("Confidence", "confidence_threshold", "float", 0.1, 0.95, 0.05),
            ("", None, "separator", 0, 0, 0),
            ("--- TRIGGERBOT ---", None, "header", 0, 0, 0),
            ("Triggerbot", "triggerbot_enabled", "bool", 0, 0, 0),
            ("Min Delay (ms)", "triggerbot_delay_min", "int", 0, 500, 10),
            ("Max Delay (ms)", "triggerbot_delay_max", "int", 0, 500, 10),
            ("", None, "separator", 0, 0, 0),
            ("--- RCS ---", None, "header", 0, 0, 0),
            ("Recoil Control", "rcs_enabled", "bool", 0, 0, 0),
            ("RCS X", "rcs_strength_x", "float", 0.0, 1.0, 0.05),
            ("RCS Y", "rcs_strength_y", "float", 0.0, 1.0, 0.05),
            ("", None, "separator", 0, 0, 0),
            ("--- VISUALS ---", None, "header", 0, 0, 0),
            ("Overlay", "overlay_enabled", "bool", 0, 0, 0),
            ("FOV Circle", "show_fov_circle", "bool", 0, 0, 0),
            ("Bounding Boxes", "show_bounding_boxes", "bool", 0, 0, 0),
            ("Snaplines", "show_snaplines", "bool", 0, 0, 0),
            ("Crosshair", "show_crosshair", "bool", 0, 0, 0),
            ("Show FPS", "show_fps", "bool", 0, 0, 0),
            ("Target Info", "show_target_info", "bool", 0, 0, 0),
            ("", None, "separator", 0, 0, 0),
            ("--- ACTIONS ---", None, "header", 0, 0, 0),
            ("Save Config", None, "action_save", 0, 0, 0),
            ("Reset Defaults", None, "action_reset", 0, 0, 0),
        ]

    def init_fonts(self):
        self.font = pygame.font.SysFont("Consolas", 14)
        self.font_header = pygame.font.SysFont("Consolas", 14, bold=True)
        self._initialized = True

    def toggle(self):
        self.visible = not self.visible

    def handle_input(self, key) -> Optional[str]:
        """Handle keyboard input. Returns action string or None."""
        if not self.visible:
            return None

        if key == pygame.K_UP:
            self._move_selection(-1)
        elif key == pygame.K_DOWN:
            self._move_selection(1)
        elif key == pygame.K_LEFT:
            self._adjust_value(-1)
        elif key == pygame.K_RIGHT:
            self._adjust_value(1)
        elif key == pygame.K_RETURN:
            return self._activate()

        return None

    def _move_selection(self, direction: int):
        """Move selection up/down, skipping headers and separators."""
        idx = self.selected_index
        for _ in range(len(self.items)):
            idx += direction
            idx %= len(self.items)
            item = self.items[idx]
            if item[2] not in ("header", "separator"):
                self.selected_index = idx
                return

    def _adjust_value(self, direction: int):
        """Adjust the currently selected value left/right."""
        item = self.items[self.selected_index]
        label, key, typ, *params = item

        if key is None:
            return

        if typ == "bool":
            self.config[key] = not self.config[key]
        elif typ == "int":
            min_val, max_val, step = params[0], params[1], params[2]
            val = self.config[key] + step * direction
            self.config[key] = max(min_val, min(max_val, val))
        elif typ == "float":
            min_val, max_val, step = params[0], params[1], params[2]
            val = round(self.config[key] + step * direction, 3)
            self.config[key] = max(min_val, min(max_val, val))
        elif typ == "choice":
            choices = params[0]
            current = self.config[key]
            try:
                idx = choices.index(current)
            except ValueError:
                idx = 0
            idx = (idx + direction) % len(choices)
            self.config[key] = choices[idx]

    def _activate(self) -> Optional[str]:
        """Handle Enter press on current item."""
        item = self.items[self.selected_index]
        label, key, typ = item[0], item[1], item[2]

        if typ == "bool" and key:
            self.config[key] = not self.config[key]
        elif typ == "action_save":
            self.config.save()
            return "saved"
        elif typ == "action_reset":
            self.config.reset()
            return "reset"
        return None

    def render(self, surface: pygame.Surface):
        """Render the menu on the given surface."""
        if not self.visible or not self._initialized:
            return

        menu_h = len(self.items) * self.ITEM_HEIGHT + self.PADDING * 2 + 30
        menu_x = (surface.get_width() - self.MENU_WIDTH) // 2
        menu_y = (surface.get_height() - menu_h) // 2

        # Background panel
        panel = pygame.Surface((self.MENU_WIDTH, menu_h), pygame.SRCALPHA)
        panel.fill(self.BACKGROUND)
        surface.blit(panel, (menu_x, menu_y))

        # Border
        pygame.draw.rect(surface, self.HEADER_COLOR,
                         (menu_x, menu_y, self.MENU_WIDTH, menu_h), 1)

        # Title
        title = self.font_header.render("CS2 AIMBOT SETTINGS", True, self.HEADER_COLOR)
        surface.blit(title, (menu_x + self.PADDING, menu_y + 8))

        # Items
        y = menu_y + 30
        for i, item in enumerate(self.items):
            label, key, typ = item[0], item[1], item[2]

            if typ == "separator":
                pygame.draw.line(surface, self.SEPARATOR_COLOR,
                                 (menu_x + self.PADDING, y + self.ITEM_HEIGHT // 2),
                                 (menu_x + self.MENU_WIDTH - self.PADDING, y + self.ITEM_HEIGHT // 2), 1)
                y += self.ITEM_HEIGHT
                continue

            if typ == "header":
                text = self.font_header.render(label, True, self.HEADER_COLOR)
                surface.blit(text, (menu_x + self.PADDING, y + 3))
                y += self.ITEM_HEIGHT
                continue

            # Selection highlight
            if i == self.selected_index:
                sel_rect = pygame.Surface((self.MENU_WIDTH - 4, self.ITEM_HEIGHT), pygame.SRCALPHA)
                sel_rect.fill((255, 255, 255, 25))
                surface.blit(sel_rect, (menu_x + 2, y))
                label_color = self.SELECTED_COLOR
            else:
                label_color = self.TEXT_COLOR

            # Label
            text = self.font.render(label, True, label_color)
            surface.blit(text, (menu_x + self.PADDING, y + 4))

            # Value
            if key is not None:
                val = self.config[key]
                if typ == "bool":
                    val_str = "ON" if val else "OFF"
                    val_color = (100, 255, 100) if val else (255, 100, 100)
                elif typ == "float":
                    val_str = f"{val:.2f}"
                    val_color = self.VALUE_COLOR
                elif typ == "int":
                    val_str = str(val)
                    val_color = self.VALUE_COLOR
                elif typ == "choice":
                    val_str = f"< {val} >"
                    val_color = self.VALUE_COLOR
                else:
                    val_str = str(val)
                    val_color = self.VALUE_COLOR

                val_text = self.font.render(val_str, True, val_color)
                surface.blit(val_text, (
                    menu_x + self.MENU_WIDTH - self.PADDING - val_text.get_width(),
                    y + 4
                ))
            elif typ.startswith("action_"):
                action_text = self.font.render("[ENTER]", True, (150, 150, 200))
                surface.blit(action_text, (
                    menu_x + self.MENU_WIDTH - self.PADDING - action_text.get_width(),
                    y + 4
                ))

            y += self.ITEM_HEIGHT
