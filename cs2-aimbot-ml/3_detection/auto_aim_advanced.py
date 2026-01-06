"""
CS2 Advanced Auto-Aim - Multi-Class
====================================
Nutzt BEIDE Klassen für perfekte Headshots!

- Class 0 (Enemy): Findet Gegner
- Class 1 (Head): Zielt auf exakten Kopf

Vorteil: Keine Schätzung mehr - AI kennt exakte Kopf-Position!
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

class AdvancedAutoAim:
    def __init__(self,
                 model_path="../models/cs2_target_detector_n/weights/best.pt",
                 confidence_threshold=0.6,
                 aim_smoothing=0.3,
                 fov_radius=300,
                 prefer_heads=True):
        """
        Advanced Auto-Aim mit Multi-Class Support

        Args:
            model_path: Pfad zum trainierten Multi-Class Model
            confidence_threshold: Minimum Confidence
            aim_smoothing: Smoothing Factor (0.1-1.0)
            fov_radius: FOV Radius in Pixel
            prefer_heads: True = Ziele auf Head-Boxen (exakt), False = Enemy-Boxen (geschätzt)
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.aim_smoothing = aim_smoothing
        self.fov_radius = fov_radius
        self.prefer_heads = prefer_heads

        # Klassen
        self.CLASS_ENEMY = 0
        self.CLASS_HEAD = 1

        # Farben
        self.COLOR_ENEMY = (0, 255, 0)
        self.COLOR_HEAD = (0, 0, 255)

        # State
        self.aim_active = False
        self.mouse_listener = None

        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.CYAN}CS2 Advanced Auto-Aim - Multi-Class")
        print(f"{Fore.GREEN}{'='*70}\n")
        print(f"{Fore.RED}⚠️  NUR FÜR OFFLINE-BOTS VERWENDEN! ⚠️\n")

        # Check Model
        if not os.path.exists(model_path):
            print(f"{Fore.RED}Model nicht gefunden: {model_path}")
            print(f"{Fore.YELLOW}Tipp: Trainiere zuerst mit Multi-Class Daten!")
            exit(1)

        # Lade Model
        print(f"{Fore.YELLOW}Lade Multi-Class Model: {Fore.CYAN}{model_path}")
        self.model = YOLO(model_path)
        print(f"{Fore.GREEN}✓ Model geladen!\n")

        # Screen Setup
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]
        self.screen_center_x = self.monitor['width'] // 2
        self.screen_center_y = self.monitor['height'] // 2

        # Stats
        self.fps = 0
        self.frame_times = []

        print(f"{Fore.WHITE}Konfiguration:")
        print(f"{Fore.WHITE}  Confidence: {Fore.CYAN}{confidence_threshold}")
        print(f"{Fore.WHITE}  Smoothing: {Fore.CYAN}{aim_smoothing}")
        print(f"{Fore.WHITE}  FOV: {Fore.CYAN}{fov_radius}px")
        print(f"{Fore.WHITE}  Priorität: {Fore.CYAN}{'Heads (exakt)' if prefer_heads else 'Enemy (geschätzt)'}")
        print(f"\n{Fore.YELLOW}Steuerung:")
        print(f"{Fore.WHITE}  RMB halten = {Fore.GREEN}AIM AKTIV")
        print(f"{Fore.WHITE}  Q = Beenden")
        print(f"\n{Fore.CYAN}Wie es funktioniert:")
        print(f"{Fore.GREEN}  1. AI erkennt Gegner (Grün) UND Köpfe (Rot)")
        print(f"{Fore.RED}  2. Zielt auf exakte Kopf-Position!")
        print(f"{Fore.YELLOW}  3. Keine Schätzung mehr - perfekte Headshots! 🎯")
        print(f"{Fore.GREEN}{'='*70}\n")

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

    def find_best_target(self, results):
        """
        Findet bestes Target

        Wenn prefer_heads=True:
          - Nutzt Head-Boxen (Class 1) - EXAKTE Position!
        Sonst:
          - Nutzt Enemy-Boxen (Class 0) und schätzt Kopf
        """
        best_target = None
        best_distance = float('inf')

        for result in results:
            boxes = result.boxes

            for box in boxes:
                conf = float(box.conf[0])
                if conf < self.confidence_threshold:
                    continue

                class_id = int(box.cls[0])

                # Filter nach Präferenz
                if self.prefer_heads and class_id != self.CLASS_HEAD:
                    continue
                elif not self.prefer_heads and class_id != self.CLASS_ENEMY:
                    continue

                # Box Koordinaten
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                # Aim-Point
                if class_id == self.CLASS_HEAD:
                    # Head-Box: Ziele auf Mitte (ist eh schon Kopf!)
                    target_x = (x1 + x2) // 2
                    target_y = (y1 + y2) // 2
                else:
                    # Enemy-Box: Schätze Kopf (25% von oben)
                    target_x = (x1 + x2) // 2
                    target_y = int(y1 + (y2 - y1) * 0.25)

                # Distanz zum Screen-Center
                distance = np.sqrt(
                    (target_x - self.screen_center_x) ** 2 +
                    (target_y - self.screen_center_y) ** 2
                )

                # FOV Check
                if distance > self.fov_radius:
                    continue

                # Wähle nähestes
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

    def draw_overlay(self, img, results, best_target):
        """Zeichnet Overlay"""
        overlay = img.copy()

        # FOV Circle
        cv2.circle(overlay, (self.screen_center_x, self.screen_center_y),
                  self.fov_radius, (255, 255, 0), 2)

        # Fadenkreuz
        cv2.drawMarker(overlay, (self.screen_center_x, self.screen_center_y),
                      (0, 255, 0), cv2.MARKER_CROSS, 30, 2)

        # Alle Detections
        for result in results:
            boxes = result.boxes

            for box in boxes:
                conf = float(box.conf[0])
                if conf < self.confidence_threshold:
                    continue

                class_id = int(box.cls[0])
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                # Farbe nach Klasse
                if class_id == self.CLASS_ENEMY:
                    color = self.COLOR_ENEMY
                    label = "Enemy"
                    thickness = 2
                else:
                    color = self.COLOR_HEAD
                    label = "Head"
                    thickness = 3

                # Aim Point
                if class_id == self.CLASS_HEAD:
                    target_x = (x1 + x2) // 2
                    target_y = (y1 + y2) // 2
                else:
                    target_x = (x1 + x2) // 2
                    target_y = int(y1 + (y2 - y1) * 0.25)

                distance = np.sqrt(
                    (target_x - self.screen_center_x) ** 2 +
                    (target_y - self.screen_center_y) ** 2
                )

                in_fov = distance <= self.fov_radius

                # Box
                cv2.rectangle(overlay, (x1, y1), (x2, y2), color, thickness)

                # Aim-Point
                cv2.drawMarker(overlay, (target_x, target_y),
                             color, cv2.MARKER_CROSS, 15, 2)

                # Label
                label_text = f"{label} {conf:.2f}"
                if in_fov:
                    label_text += f" [{int(distance)}px]"

                cv2.putText(overlay, label_text, (x1, y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Best Target
        if best_target:
            target_x, target_y, conf, distance, class_id = best_target

            # Rotes Kreuz
            cv2.drawMarker(overlay, (target_x, target_y),
                         (0, 0, 255), cv2.MARKER_CROSS, 25, 3)

            # Linie
            cv2.line(overlay,
                    (self.screen_center_x, self.screen_center_y),
                    (target_x, target_y),
                    (0, 0, 255), 2)

            # Target Info
            class_name = "HEAD" if class_id == self.CLASS_HEAD else "ENEMY"
            target_info = f"TARGET: {class_name}"
            cv2.putText(overlay, target_info, (target_x + 15, target_y),
                       cv2.FONT_HERSHEY_BOLD, 0.6, (0, 0, 255), 2)

        return overlay

    def run(self):
        """Hauptloop"""
        print(f"{Fore.GREEN}Advanced Auto-Aim aktiv!\n")

        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.mouse_listener.start()

        frame_count = 0
        start_time = time.time()

        try:
            while True:
                loop_start = time.time()

                # Capture
                screen = self.capture_screen()

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
                    class_name = "HEAD" if class_id == self.CLASS_HEAD else "ENEMY"
                    cv2.putText(display, f"Target: {class_name} {conf:.2f} ({int(distance)}px)",
                               (10, info_y + 80),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                mode_text = "Mode: HEAD Priority" if self.prefer_heads else "Mode: ENEMY Priority"
                cv2.putText(display, mode_text, (10, info_y + 120),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

                cv2.putText(display, "Q = Quit", (10, info_y + 160),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                # Display
                scale = 0.6
                width = int(display.shape[1] * scale)
                height = int(display.shape[0] * scale)
                display_resized = cv2.resize(display, (width, height))

                cv2.imshow('CS2 Advanced Auto-Aim', display_resized)

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

            total_time = time.time() - start_time
            avg_fps = frame_count / total_time if total_time > 0 else 0

            print(f"\n{Fore.GREEN}{'='*70}")
            print(f"{Fore.CYAN}Session Stats:")
            print(f"{Fore.WHITE}  Frames: {Fore.CYAN}{frame_count}")
            print(f"{Fore.WHITE}  Avg FPS: {Fore.CYAN}{avg_fps:.1f}")
            print(f"{Fore.WHITE}  Runtime: {Fore.CYAN}{total_time:.1f}s")
            print(f"{Fore.GREEN}{'='*70}\n")

def main():
    # Finde Model
    model_path = "../models/cs2_target_detector_n/weights/best.pt"

    if not os.path.exists(model_path):
        models_dir = "../models"
        if os.path.exists(models_dir):
            runs = [d for d in os.listdir(models_dir) if d.startswith("cs2_target_detector")]
            if runs:
                latest_run = sorted(runs)[-1]
                model_path = os.path.join(models_dir, latest_run, "weights", "best.pt")

    # Starte Advanced Auto-Aim
    auto_aim = AdvancedAutoAim(
        model_path=model_path,
        confidence_threshold=0.6,
        aim_smoothing=0.3,
        fov_radius=300,
        prefer_heads=True       # True = Zielt auf Head-Boxen (EXAKT!)
                                # False = Zielt auf Enemy-Boxen (geschätzt)
    )

    auto_aim.run()

if __name__ == "__main__":
    main()
