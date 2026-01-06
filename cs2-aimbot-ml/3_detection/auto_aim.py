"""
CS2 Auto-Aim System
===================
Bewegt die Maus automatisch auf erkannte Gegner.

⚠️ NUR FÜR OFFLINE-BOTS VERWENDEN! ⚠️

Features:
- Automatische Gegner-Erkennung
- Maus-Bewegung zum nächsten Gegner
- Headshot-Priorisierung (Kopf ist oben in der Bounding Box)
- Aktivierung per Hotkey (rechte Maustaste)
- Smooth Aim (sieht natürlicher aus)

Verwendung:
    python auto_aim.py

Steuerung:
    Rechte Maustaste gedrückt halten = Aim-Assist aktiv
    Q = Beenden
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
import win32api
import win32con
import ctypes

init(autoreset=True)

# Deaktiviere PyAutoGUI Failsafe für smoother Bewegung
pyautogui.FAILSAFE = False

class AutoAim:
    def __init__(self,
                 model_path="../models/cs2_target_detector_n/weights/best.pt",
                 confidence_threshold=0.6,
                 aim_smoothing=0.3,
                 headshot_offset=0.25,
                 fov_radius=300):
        """
        CS2 Auto-Aim System

        Args:
            model_path: Pfad zum trainierten Model
            confidence_threshold: Minimum Confidence für Detections
            aim_smoothing: Wie smooth die Maus bewegt wird (0.0-1.0, kleiner = smoother)
            headshot_offset: Wo innerhalb der Box gezielt wird (0.0=oben/Kopf, 0.5=Mitte, 1.0=unten)
            fov_radius: Maximale Distanz zum Fadenkreuz (Pixel) um Target zu berücksichtigen
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.aim_smoothing = aim_smoothing
        self.headshot_offset = headshot_offset
        self.fov_radius = fov_radius

        # Aim-Assist state
        self.aim_active = False
        self.mouse_listener = None

        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.CYAN}CS2 Auto-Aim System")
        print(f"{Fore.GREEN}{'='*70}\n")

        print(f"{Fore.RED}⚠️  NUR FÜR OFFLINE-BOTS VERWENDEN! ⚠️\n")

        # Check ob Model existiert
        if not os.path.exists(model_path):
            print(f"{Fore.RED}Model nicht gefunden: {model_path}")
            print(f"{Fore.YELLOW}Tipp: Trainiere zuerst ein Model mit train_model.py!")
            exit(1)

        # Lade Model
        print(f"{Fore.YELLOW}Lade Model: {Fore.CYAN}{model_path}")
        self.model = YOLO(model_path)
        print(f"{Fore.GREEN}✓ Model geladen!\n")

        # Screen Capture Setup
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]

        # Screen-Mitte (Fadenkreuz-Position)
        self.screen_center_x = self.monitor['width'] // 2
        self.screen_center_y = self.monitor['height'] // 2

        # Stats
        self.fps = 0
        self.frame_times = []

        print(f"{Fore.WHITE}Konfiguration:")
        print(f"{Fore.WHITE}  Confidence Threshold: {Fore.CYAN}{confidence_threshold}")
        print(f"{Fore.WHITE}  Aim Smoothing: {Fore.CYAN}{aim_smoothing}")
        print(f"{Fore.WHITE}  Headshot Offset: {Fore.CYAN}{headshot_offset} {Fore.WHITE}(0.0=Kopf, 0.5=Mitte)")
        print(f"{Fore.WHITE}  FOV Radius: {Fore.CYAN}{fov_radius}px")
        print(f"{Fore.WHITE}  Screen Center: {Fore.CYAN}{self.screen_center_x}x{self.screen_center_y}")

        print(f"\n{Fore.YELLOW}Steuerung:")
        print(f"{Fore.WHITE}  Rechte Maustaste gedrückt halten = {Fore.GREEN}AIM AKTIV")
        print(f"{Fore.WHITE}  Loslassen = Deaktiviert")
        print(f"{Fore.WHITE}  Q = Beenden")

        print(f"\n{Fore.CYAN}Tipps:")
        print(f"{Fore.WHITE}  • Halte rechte Maustaste während du auf Gegner zielst")
        print(f"{Fore.WHITE}  • Die AI zieht automatisch auf den Kopf")
        print(f"{Fore.WHITE}  • Du musst nur noch abdrücken!")

        print(f"{Fore.GREEN}{'='*70}\n")

    def on_click(self, x, y, button, pressed):
        """Mouse-Event Handler"""
        if button == mouse.Button.right:
            self.aim_active = pressed
            if pressed:
                print(f"{Fore.GREEN}🎯 AIM ASSIST AKTIV")
            else:
                print(f"{Fore.YELLOW}⊙ Aim Assist deaktiviert")

    def capture_screen(self):
        """Macht einen Screenshot"""
        screenshot = self.sct.grab(self.monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    def find_best_target(self, results):
        """
        Findet das beste Target zum Anzielen

        Priorisiert:
        1. Targets näher am Fadenkreuz (innerhalb FOV)
        2. Höhere Confidence
        3. Näher am Screen-Center

        Returns:
            (x, y) Koordinaten zum Anzielen, oder None
        """
        best_target = None
        best_distance = float('inf')

        for result in results:
            boxes = result.boxes

            for box in boxes:
                conf = float(box.conf[0])
                if conf < self.confidence_threshold:
                    continue

                # Box Koordinaten
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                # Berechne Aim-Point (Kopf = oben in der Box)
                target_x = (x1 + x2) // 2
                # headshot_offset: 0.0 = ganz oben (Kopf), 0.5 = Mitte, 1.0 = Füße
                target_y = int(y1 + (y2 - y1) * self.headshot_offset)

                # Distanz zum Screen-Center (Fadenkreuz)
                distance = np.sqrt(
                    (target_x - self.screen_center_x) ** 2 +
                    (target_y - self.screen_center_y) ** 2
                )

                # Nur Targets innerhalb des FOV
                if distance > self.fov_radius:
                    continue

                # Wähle nähestes Target
                if distance < best_distance:
                    best_distance = distance
                    best_target = (target_x, target_y, conf, distance)

        return best_target

    def move_mouse_smooth(self, target_x, target_y):
        """
        Bewegt die Maus smooth zum Target

        Args:
            target_x, target_y: Ziel-Koordinaten auf dem Screen
        """
        # Aktuelle Maus-Position
        current_x, current_y = pyautogui.position()

        # Berechne Differenz
        delta_x = target_x - current_x
        delta_y = target_y - current_y

        # Smooth Movement (nur ein Teil der Distanz bewegen)
        move_x = int(delta_x * self.aim_smoothing)
        move_y = int(delta_y * self.aim_smoothing)

        # Bewege Maus relativ
        if abs(move_x) > 1 or abs(move_y) > 1:
            # Nutze Windows API für präzisere Kontrolle
            ctypes.windll.user32.mouse_event(1, move_x, move_y, 0, 0)

    def draw_overlay(self, img, results, best_target):
        """Zeichnet Debug-Overlay"""
        overlay = img.copy()

        # FOV Circle (zeigt Erfassungsbereich)
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

                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                # Aim Point
                target_x = (x1 + x2) // 2
                target_y = int(y1 + (y2 - y1) * self.headshot_offset)

                # Farbe: Grün wenn innerhalb FOV, Gelb sonst
                distance = np.sqrt(
                    (target_x - self.screen_center_x) ** 2 +
                    (target_y - self.screen_center_y) ** 2
                )

                in_fov = distance <= self.fov_radius
                color = (0, 255, 0) if in_fov else (0, 165, 255)

                # Box
                cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)

                # Aim-Point Marker
                cv2.drawMarker(overlay, (target_x, target_y),
                             color, cv2.MARKER_CROSS, 15, 2)

                # Label
                label = f"Enemy {conf:.2f}"
                if in_fov:
                    label += f" [{int(distance)}px]"

                cv2.putText(overlay, label, (x1, y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Best Target Highlight
        if best_target:
            target_x, target_y, conf, distance = best_target

            # Rotes Kreuz auf dem Ziel
            cv2.drawMarker(overlay, (target_x, target_y),
                         (0, 0, 255), cv2.MARKER_CROSS, 25, 3)

            # Linie vom Fadenkreuz zum Ziel
            cv2.line(overlay,
                    (self.screen_center_x, self.screen_center_y),
                    (target_x, target_y),
                    (0, 0, 255), 2)

        return overlay

    def run(self):
        """Hauptloop"""
        print(f"{Fore.GREEN}Auto-Aim System aktiv!\n")

        # Starte Mouse Listener
        self.mouse_listener = mouse.Listener(on_click=self.on_click)
        self.mouse_listener.start()

        frame_count = 0
        start_time = time.time()

        try:
            while True:
                loop_start = time.time()

                # Capture Screen
                screen = self.capture_screen()

                # Run Detection
                results = self.model(screen, verbose=False, conf=self.confidence_threshold)

                # Finde bestes Target
                best_target = self.find_best_target(results)

                # Wenn Aim aktiv und Target gefunden → bewege Maus
                if self.aim_active and best_target:
                    target_x, target_y, conf, distance = best_target
                    self.move_mouse_smooth(target_x, target_y)

                # Draw Overlay
                display = self.draw_overlay(screen, results, best_target)

                # FPS Counter
                self.frame_times.append(time.time() - loop_start)
                if len(self.frame_times) > 30:
                    self.frame_times.pop(0)
                self.fps = 1.0 / (sum(self.frame_times) / len(self.frame_times))

                # Info Overlay
                info_y = 30

                # Aim Status
                aim_status = "AIM ACTIVE" if self.aim_active else "Aim Inactive"
                aim_color = (0, 255, 0) if self.aim_active else (100, 100, 100)
                cv2.putText(display, aim_status, (10, info_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, aim_color, 3)

                # FPS
                cv2.putText(display, f"FPS: {self.fps:.1f}", (10, info_y + 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                # Target Info
                if best_target:
                    _, _, conf, distance = best_target
                    cv2.putText(display, f"Target: {conf:.2f} ({int(distance)}px)",
                               (10, info_y + 80),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # Controls
                cv2.putText(display, "RMB = Aim | Q = Quit", (10, info_y + 120),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                # Resize für Display
                scale = 0.6
                width = int(display.shape[1] * scale)
                height = int(display.shape[0] * scale)
                display_resized = cv2.resize(display, (width, height))

                cv2.imshow('CS2 Auto-Aim', display_resized)

                # Tastatur Check
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break

                frame_count += 1

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Beendet durch Benutzer")

        finally:
            if self.mouse_listener:
                self.mouse_listener.stop()
            cv2.destroyAllWindows()

            total_time = time.time() - start_time
            avg_fps = frame_count / total_time if total_time > 0 else 0

            print(f"\n{Fore.GREEN}{'='*70}")
            print(f"{Fore.CYAN}Session Statistiken:")
            print(f"{Fore.WHITE}  Frames: {Fore.CYAN}{frame_count}")
            print(f"{Fore.WHITE}  Durchschnitt FPS: {Fore.CYAN}{avg_fps:.1f}")
            print(f"{Fore.WHITE}  Laufzeit: {Fore.CYAN}{total_time:.1f}s")
            print(f"{Fore.GREEN}{'='*70}\n")

def main():
    """Main Function"""

    # Finde Model automatisch
    model_path = "../models/cs2_target_detector_n/weights/best.pt"

    if not os.path.exists(model_path):
        models_dir = "../models"
        if os.path.exists(models_dir):
            runs = [d for d in os.listdir(models_dir) if d.startswith("cs2_target_detector")]
            if runs:
                latest_run = sorted(runs)[-1]
                model_path = os.path.join(models_dir, latest_run, "weights", "best.pt")

    # Starte Auto-Aim
    auto_aim = AutoAim(
        model_path=model_path,
        confidence_threshold=0.6,    # Nur sichere Detections
        aim_smoothing=0.3,            # 0.1 = sehr smooth, 1.0 = instant snap
        headshot_offset=0.25,         # 0.0 = Kopf, 0.5 = Brust, 1.0 = Füße
        fov_radius=300                # Max Distanz vom Fadenkreuz (Pixel)
    )

    auto_aim.run()

if __name__ == "__main__":
    main()
