"""
CS2 Team-Aware Auto-Aim
========================
Erkennt dein Team und zielt NUR auf Gegner!

Features:
- Automatische Team-Erkennung (Blau = CT, Orange = T)
- Zielt nur auf gegnerisches Team
- Nutzt Head/Legs für präzises Aiming
- Vermeidet Friendly Fire!
"""

import cv2
import numpy as np
import mss
import time
from ultralytics import YOLO
from colorama import Fore, init
import os
import pyautogui
from pynput import mouse
import ctypes

init(autoreset=True)
pyautogui.FAILSAFE = False

class TeamAwareAutoAim:
    def __init__(self,
                 model_path="../models/cs2_target_detector_n/weights/best.pt",
                 confidence_threshold=0.6,
                 aim_smoothing=0.3,
                 fov_radius=300):

        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.aim_smoothing = aim_smoothing
        self.fov_radius = fov_radius

        # Klassen
        self.CLASS_ENEMY_CT = 0
        self.CLASS_ENEMY_T = 1
        self.CLASS_HEAD = 2
        self.CLASS_LEGS = 3

        # Team Detection
        self.player_team = None  # 'CT' oder 'T'
        self.team_check_cooldown = 0

        # Farben
        self.COLOR_CT = (255, 100, 0)
        self.COLOR_T = (0, 165, 255)
        self.COLOR_HEAD = (0, 0, 255)
        self.COLOR_LEGS = (255, 0, 255)

        # State
        self.aim_active = False
        self.mouse_listener = None

        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.CYAN}CS2 Team-Aware Auto-Aim")
        print(f"{Fore.GREEN}{'='*70}\n")
        print(f"{Fore.RED}⚠️  NUR FÜR OFFLINE-BOTS! ⚠️\n")

        if not os.path.exists(model_path):
            print(f"{Fore.RED}Model nicht gefunden!")
            exit(1)

        print(f"{Fore.YELLOW}Lade Team-Aware Model...")
        self.model = YOLO(model_path)
        print(f"{Fore.GREEN}✓ Model geladen!\n")

        # Screen
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]
        self.screen_center_x = self.monitor['width'] // 2
        self.screen_center_y = self.monitor['height'] // 2

        # UI-Bereich für Team-Detection (oben links)
        self.ui_region = {
            'left': self.monitor['left'],
            'top': self.monitor['top'],
            'width': 200,
            'height': 150
        }

        self.fps = 0
        self.frame_times = []

        print(f"{Fore.WHITE}Konfiguration:")
        print(f"{Fore.WHITE}  Confidence: {Fore.CYAN}{confidence_threshold}")
        print(f"{Fore.WHITE}  Smoothing: {Fore.CYAN}{aim_smoothing}")
        print(f"{Fore.WHITE}  FOV: {Fore.CYAN}{fov_radius}px")
        print(f"\n{Fore.CYAN}Team-Detection:")
        print(f"{Fore.BLUE}  • Blau UI = Du bist CT → Ziele auf T")
        print(f"{Fore.YELLOW}  • Orange UI = Du bist T → Ziele auf CT")
        print(f"{Fore.GREEN}  → Kein Friendly Fire!")
        print(f"\n{Fore.YELLOW}Steuerung:")
        print(f"{Fore.WHITE}  RMB halten = AIM AKTIV")
        print(f"{Fore.WHITE}  Q = Beenden")
        print(f"{Fore.GREEN}{'='*70}\n")

    def detect_player_team(self, screen):
        """
        Erkennt Team des Spielers anhand UI-Farbe oben links

        Returns:
            'CT' wenn blau, 'T' wenn orange/gelb
        """
        # Schneide UI-Bereich aus (oben links)
        ui_area = screen[0:150, 0:200]

        # Konvertiere zu HSV für bessere Farberkennung
        hsv = cv2.cvtColor(ui_area, cv2.COLOR_BGR2HSV)

        # Blau-Maske (CT)
        lower_blue = np.array([90, 50, 50])
        upper_blue = np.array([130, 255, 255])
        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
        blue_pixels = cv2.countNonZero(blue_mask)

        # Orange/Gelb-Maske (T)
        lower_orange = np.array([10, 100, 100])
        upper_orange = np.array([30, 255, 255])
        orange_mask = cv2.inRange(hsv, lower_orange, upper_orange)
        orange_pixels = cv2.countNonZero(orange_mask)

        # Welche Farbe dominiert?
        if blue_pixels > orange_pixels and blue_pixels > 100:
            return 'CT'
        elif orange_pixels > blue_pixels and orange_pixels > 100:
            return 'T'
        else:
            return None  # Unsicher

    def on_click(self, x, y, button, pressed):
        """Mouse Handler"""
        if button == mouse.Button.right:
            self.aim_active = pressed
            if pressed:
                print(f"{Fore.GREEN}🎯 AIM ASSIST AKTIV")
            else:
                print(f"{Fore.YELLOW}⊙ Aim Assist deaktiviert")

    def capture_screen(self):
        """Screenshot"""
        screenshot = self.sct.grab(self.monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    def is_valid_target(self, class_id):
        """
        Prüft ob Target gültig ist (nicht eigenes Team!)

        Args:
            class_id: Erkannte Klasse
        Returns:
            True wenn gegnerisch, False wenn eigenes Team
        """
        if self.player_team is None:
            return False  # Team noch nicht erkannt

        # Wenn Spieler CT ist, nur auf T zielen
        if self.player_team == 'CT' and class_id == self.CLASS_ENEMY_T:
            return True

        # Wenn Spieler T ist, nur auf CT zielen
        if self.player_team == 'T' and class_id == self.CLASS_ENEMY_CT:
            return True

        # Head/Legs sind immer OK (beide Teams)
        if class_id in [self.CLASS_HEAD, self.CLASS_LEGS]:
            return True

        return False

    def find_best_target(self, results):
        """Findet bestes Target (nur gegnerisches Team!)"""
        best_target = None
        best_distance = float('inf')

        for result in results:
            boxes = result.boxes

            for box in boxes:
                conf = float(box.conf[0])
                if conf < self.confidence_threshold:
                    continue

                class_id = int(box.cls[0])

                # WICHTIG: Nur gültige Targets (kein eigenes Team!)
                if not self.is_valid_target(class_id):
                    continue

                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                # Aim-Point je nach Klasse
                if class_id == self.CLASS_HEAD:
                    target_x = (x1 + x2) // 2
                    target_y = (y1 + y2) // 2
                elif class_id == self.CLASS_LEGS:
                    target_x = (x1 + x2) // 2
                    target_y = (y1 + y2) // 2
                else:  # Enemy Body
                    target_x = (x1 + x2) // 2
                    target_y = int(y1 + (y2 - y1) * 0.25)  # Geschätzter Kopf

                distance = np.sqrt(
                    (target_x - self.screen_center_x) ** 2 +
                    (target_y - self.screen_center_y) ** 2
                )

                if distance > self.fov_radius:
                    continue

                if distance < best_distance:
                    best_distance = distance
                    best_target = (target_x, target_y, conf, distance, class_id)

        return best_target

    def move_mouse_smooth(self, target_x, target_y):
        """Smooth Mouse Movement"""
        current_x, current_y = pyautogui.position()

        delta_x = target_x - current_x
        delta_y = target_y - current_y

        move_x = int(delta_x * self.aim_smoothing)
        move_y = int(delta_y * self.aim_smoothing)

        if abs(move_x) > 1 or abs(move_y) > 1:
            ctypes.windll.user32.mouse_event(1, move_x, move_y, 0, 0)

    def get_class_color(self, class_id):
        """Farbe für Klasse"""
        colors = {
            self.CLASS_ENEMY_CT: self.COLOR_CT,
            self.CLASS_ENEMY_T: self.COLOR_T,
            self.CLASS_HEAD: self.COLOR_HEAD,
            self.CLASS_LEGS: self.COLOR_LEGS
        }
        return colors.get(class_id, (255, 255, 255))

    def get_class_name(self, class_id):
        """Name für Klasse"""
        names = {
            self.CLASS_ENEMY_CT: "Enemy CT",
            self.CLASS_ENEMY_T: "Enemy T",
            self.CLASS_HEAD: "Head",
            self.CLASS_LEGS: "Legs"
        }
        return names.get(class_id, "Unknown")

    def draw_overlay(self, img, results, best_target):
        """Zeichnet Overlay"""
        overlay = img.copy()

        # Team-Info oben rechts
        team_text = f"YOUR TEAM: {self.player_team if self.player_team else 'DETECTING...'}"
        team_color = self.COLOR_CT if self.player_team == 'CT' else self.COLOR_T
        cv2.putText(overlay, team_text, (img.shape[1] - 300, 30),
                   cv2.FONT_HERSHEY_BOLD, 0.7, team_color if self.player_team else (255, 255, 255), 2)

        # FOV Circle
        cv2.circle(overlay, (self.screen_center_x, self.screen_center_y),
                  self.fov_radius, (255, 255, 0), 2)

        # Fadenkreuz
        cv2.drawMarker(overlay, (self.screen_center_x, self.screen_center_y),
                      (0, 255, 0), cv2.MARKER_CROSS, 30, 2)

        # Detections
        for result in results:
            boxes = result.boxes

            for box in boxes:
                conf = float(box.conf[0])
                if conf < self.confidence_threshold:
                    continue

                class_id = int(box.cls[0])
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                color = self.get_class_color(class_id)

                # Markiere invalide Targets (eigenes Team) anders
                is_valid = self.is_valid_target(class_id)
                thickness = 2 if is_valid else 1
                line_type = cv2.LINE_AA if is_valid else cv2.LINE_4

                cv2.rectangle(overlay, (x1, y1), (x2, y2), color, thickness, line_type)

                # Label
                label = self.get_class_name(class_id)
                if not is_valid and class_id in [self.CLASS_ENEMY_CT, self.CLASS_ENEMY_T]:
                    label += " (TEAM!)"
                    color = (128, 128, 128)  # Grau für eigenes Team

                cv2.putText(overlay, label, (x1, y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Best Target
        if best_target:
            target_x, target_y, conf, distance, class_id = best_target

            cv2.drawMarker(overlay, (target_x, target_y),
                         (0, 0, 255), cv2.MARKER_CROSS, 25, 3)

            cv2.line(overlay,
                    (self.screen_center_x, self.screen_center_y),
                    (target_x, target_y),
                    (0, 0, 255), 2)

        return overlay

    def run(self):
        """Hauptloop"""
        print(f"{Fore.GREEN}Team-Aware Auto-Aim aktiv!\n")

        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.mouse_listener.start()

        frame_count = 0
        start_time = time.time()

        try:
            while True:
                loop_start = time.time()

                screen = self.capture_screen()

                # Team-Detection alle 60 Frames
                if frame_count % 60 == 0:
                    detected_team = self.detect_player_team(screen)
                    if detected_team and detected_team != self.player_team:
                        self.player_team = detected_team
                        team_color = Fore.BLUE if detected_team == 'CT' else Fore.YELLOW
                        print(f"\n{team_color}► Team erkannt: {detected_team}")
                        if detected_team == 'CT':
                            print(f"{Fore.GREEN}  → Ziele auf Terroristen (Orange)")
                        else:
                            print(f"{Fore.GREEN}  → Ziele auf Counter-Terrorists (Blau)\n")

                # Detection
                results = self.model(screen, verbose=False, conf=self.confidence_threshold)

                # Finde Target
                best_target = self.find_best_target(results)

                # Aim
                if self.aim_active and best_target:
                    target_x, target_y, conf, distance, class_id = best_target
                    self.move_mouse_smooth(target_x, target_y)

                # Overlay
                display = self.draw_overlay(screen, results, best_target)

                # FPS
                self.frame_times.append(time.time() - loop_start)
                if len(self.frame_times) > 30:
                    self.frame_times.pop(0)
                self.fps = 1.0 / (sum(self.frame_times) / len(self.frame_times))

                # Info
                info_y = 30
                aim_status = "AIM ACTIVE" if self.aim_active else "Aim Inactive"
                aim_color = (0, 255, 0) if self.aim_active else (100, 100, 100)
                cv2.putText(display, aim_status, (10, info_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, aim_color, 3)

                cv2.putText(display, f"FPS: {self.fps:.1f}", (10, info_y + 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                if best_target:
                    _, _, conf, distance, class_id = best_target
                    class_name = self.get_class_name(class_id)
                    cv2.putText(display, f"Target: {class_name} {conf:.2f}",
                               (10, info_y + 80),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # Display
                scale = 0.6
                width = int(display.shape[1] * scale)
                height = int(display.shape[0] * scale)
                display_resized = cv2.resize(display, (width, height))

                cv2.imshow('CS2 Team-Aware Auto-Aim', display_resized)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break

                frame_count += 1

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Beendet")

        finally:
            if self.mouse_listener:
                self.mouse_listener.stop()
            cv2.destroyAllWindows()

            print(f"\n{Fore.GREEN}{'='*70}")
            print(f"{Fore.CYAN}Session Stats:")
            print(f"{Fore.WHITE}  Team: {Fore.CYAN}{self.player_team}")
            print(f"{Fore.WHITE}  Frames: {Fore.CYAN}{frame_count}")
            print(f"{Fore.GREEN}{'='*70}\n")

def main():
    model_path = "../models/cs2_target_detector_n/weights/best.pt"

    if not os.path.exists(model_path):
        models_dir = "../models"
        if os.path.exists(models_dir):
            runs = [d for d in os.listdir(models_dir) if d.startswith("cs2_target_detector")]
            if runs:
                latest_run = sorted(runs)[-1]
                model_path = os.path.join(models_dir, latest_run, "weights", "best.pt")

    auto_aim = TeamAwareAutoAim(
        model_path=model_path,
        confidence_threshold=0.6,
        aim_smoothing=0.3,
        fov_radius=300
    )

    auto_aim.run()

if __name__ == "__main__":
    main()
