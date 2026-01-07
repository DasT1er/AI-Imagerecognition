"""
CS2 Auto-Aim mit 6-Class Team-Aware System
===========================================
Features:
- 6 Klassen: CT Body/Head/Legs, T Body/Head/Legs
- Erweiterte Team-Erkennung:
  1. UI-Farbe (blau/orange)
  2. Icons über Spielern
  3. Crosshair-Kreis mit X (Teammate-Indicator)
- Friendly Fire Prevention
- Präzises Head-Aiming
"""

import cv2
import numpy as np
import pyautogui
import time
import mss
import os
from ultralytics import YOLO
from colorama import Fore, init
import torch

init(autoreset=True)

class SixClassAutoAim:
    def __init__(self, model_path="best.pt"):
        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.CYAN}CS2 6-Class Auto-Aim System")
        print(f"{Fore.GREEN}{'='*70}\n")

        # Model laden
        print(f"{Fore.CYAN}Lade Model: {Fore.WHITE}{model_path}")
        self.model = YOLO(model_path)

        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"{Fore.CYAN}Device: {Fore.WHITE}{device}")

        if device == 'cuda':
            print(f"{Fore.GREEN}✓ GPU Acceleration aktiv")

        # Klassen
        self.CLASS_CT_BODY = 0
        self.CLASS_CT_HEAD = 1
        self.CLASS_CT_LEGS = 2
        self.CLASS_T_BODY = 3
        self.CLASS_T_HEAD = 4
        self.CLASS_T_LEGS = 5

        # Config
        self.confidence_threshold = 0.4
        self.fov_radius = 300  # Pixel um Crosshair
        self.smooth_factor = 0.25  # Aiming smoothness
        self.head_priority = True  # Head vor Body bevorzugen

        # State
        self.player_team = None
        self.last_team_check = 0
        self.team_check_interval = 1.0  # Sekunden

        # Screenshot
        self.sct = mss.mss()

        # Monitor-Auswahl
        self.monitor = self.select_monitor()

        # Screen center
        self.screen_center = (self.monitor['width'] // 2, self.monitor['height'] // 2)

        print(f"\n{Fore.YELLOW}Konfiguration:")
        print(f"  Confidence:     {self.confidence_threshold}")
        print(f"  FOV Radius:     {self.fov_radius}px")
        print(f"  Smooth Factor:  {self.smooth_factor}")
        print(f"  Head Priority:  {self.head_priority}")
        print(f"\n{Fore.GREEN}{'='*70}\n")
        print(f"{Fore.CYAN}Steuerung:")
        print(f"  SHIFT gedrückt  - Auto-Aim aktiv")
        print(f"  Q               - Beenden")
        print(f"\n{Fore.YELLOW}Team-Erkennung:")
        print(f"  • UI-Farbe (Blau=CT, Orange=T)")
        print(f"  • Icons über Spielern")
        print(f"  • Crosshair-Kreis mit X (Teammates)")
        print(f"\n{Fore.GREEN}{'='*70}\n")

    def select_monitor(self):
        """Lässt User Monitor auswählen"""
        monitors = self.sct.monitors

        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.CYAN}Monitor-Auswahl")
        print(f"{Fore.GREEN}{'='*70}\n")

        print(f"{Fore.YELLOW}Verfügbare Monitore:\n")

        # Monitor 0 ist "All Monitors" - überspringen
        for i in range(1, len(monitors)):
            mon = monitors[i]
            print(f"{Fore.CYAN}[{i}] {Fore.WHITE}Monitor {i}")
            print(f"    Auflösung: {mon['width']}x{mon['height']}")
            print(f"    Position: X={mon['left']}, Y={mon['top']}")
            print()

        # User Input
        while True:
            try:
                choice = input(f"{Fore.YELLOW}Wähle Monitor (1-{len(monitors)-1}): {Fore.WHITE}")
                monitor_num = int(choice)

                if 1 <= monitor_num < len(monitors):
                    selected = monitors[monitor_num]
                    print(f"\n{Fore.GREEN}✓ Monitor {monitor_num} gewählt!")
                    print(f"  {selected['width']}x{selected['height']}\n")
                    return selected
                else:
                    print(f"{Fore.RED}Ungültige Auswahl! Wähle zwischen 1 und {len(monitors)-1}")
            except ValueError:
                print(f"{Fore.RED}Bitte eine Zahl eingeben!")
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Abgebrochen.")
                exit(0)

    def detect_player_team(self, screen):
        """
        Erweiterte Team-Erkennung mit mehreren Methoden
        """
        # Methode 1: UI-Farbe oben links
        ui_area = screen[0:150, 0:200]
        hsv = cv2.cvtColor(ui_area, cv2.COLOR_BGR2HSV)

        # Blue mask (CT)
        lower_blue = np.array([90, 50, 50])
        upper_blue = np.array([130, 255, 255])
        blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
        blue_pixels = cv2.countNonZero(blue_mask)

        # Orange/Yellow mask (T)
        lower_orange = np.array([10, 100, 100])
        upper_orange = np.array([30, 255, 255])
        orange_mask = cv2.inRange(hsv, lower_orange, upper_orange)
        orange_pixels = cv2.countNonZero(orange_mask)

        if blue_pixels > orange_pixels and blue_pixels > 100:
            return 'CT'
        elif orange_pixels > blue_pixels and orange_pixels > 100:
            return 'T'

        # Fallback: Letzte bekannte Team-Info
        return self.player_team

    def detect_teammate_indicator(self, screen, x, y, width, height):
        """
        Erkennt Teammate-Indikatoren:
        - Icon über Kopf
        - Crosshair-Kreis mit X
        """
        h, w = screen.shape[:2]

        # Region über dem Spieler prüfen (für Icon)
        icon_y1 = max(0, y - 80)
        icon_y2 = max(0, y - 10)
        icon_x1 = max(0, x)
        icon_x2 = min(w, x + width)

        if icon_y1 < icon_y2 and icon_x1 < icon_x2:
            icon_region = screen[icon_y1:icon_y2, icon_x1:icon_x2]

            # Prüfe auf farbige Icons (blau oder gelb/orange)
            hsv = cv2.cvtColor(icon_region, cv2.COLOR_BGR2HSV)

            # Blau für CT Teammates
            blue_mask = cv2.inRange(hsv, np.array([90, 50, 50]), np.array([130, 255, 255]))
            blue_count = cv2.countNonZero(blue_mask)

            # Gelb/Orange für T Teammates
            yellow_mask = cv2.inRange(hsv, np.array([15, 100, 100]), np.array([35, 255, 255]))
            yellow_count = cv2.countNonZero(yellow_mask)

            # Wenn starke Farbpräsenz = wahrscheinlich Teammate
            if blue_count > 50 or yellow_count > 50:
                return True

        # Center Crosshair Bereich prüfen (für X-Symbol)
        cx, cy = self.screen_center
        crosshair_size = 80

        ch_x1 = max(0, cx - crosshair_size)
        ch_x2 = min(w, cx + crosshair_size)
        ch_y1 = max(0, cy - crosshair_size)
        ch_y2 = min(h, cy + crosshair_size)

        # Prüfe ob Spieler in Crosshair-Nähe
        player_cx = x + width // 2
        player_cy = y + height // 2

        if ch_x1 <= player_cx <= ch_x2 and ch_y1 <= player_cy <= ch_y2:
            crosshair_region = screen[ch_y1:ch_y2, ch_x1:ch_x2]

            # Suche nach Kreis mit X (X ist oft dunkel auf hellem Kreis)
            gray = cv2.cvtColor(crosshair_region, cv2.COLOR_BGR2GRAY)

            # Kreise erkennen
            circles = cv2.HoughCircles(
                gray,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=50,
                param1=100,
                param2=30,
                minRadius=15,
                maxRadius=40
            )

            if circles is not None:
                # Kreis gefunden = wahrscheinlich Teammate-Indicator
                return True

        return False

    def is_valid_target(self, class_id, screen, bbox):
        """
        Prüft ob Target gültig ist (gegnerisches Team)
        """
        if self.player_team is None:
            return False

        x, y, w, h = bbox

        # Prüfe auf Teammate-Indikatoren
        if self.detect_teammate_indicator(screen, x, y, w, h):
            return False  # Hat Teammate-Icon = nicht schießen!

        # Klassen-basierte Team-Prüfung
        if self.player_team == 'CT':
            # Wir sind CT, nur auf T zielen
            return class_id in [self.CLASS_T_BODY, self.CLASS_T_HEAD, self.CLASS_T_LEGS]
        elif self.player_team == 'T':
            # Wir sind T, nur auf CT zielen
            return class_id in [self.CLASS_CT_BODY, self.CLASS_CT_HEAD, self.CLASS_CT_LEGS]

        return False

    def get_target_priority(self, class_id):
        """
        Gibt Priorität für Target-Typ zurück
        Head > Body > Legs
        """
        if class_id in [self.CLASS_CT_HEAD, self.CLASS_T_HEAD]:
            return 3  # Höchste Priorität
        elif class_id in [self.CLASS_CT_BODY, self.CLASS_T_BODY]:
            return 2
        elif class_id in [self.CLASS_CT_LEGS, self.CLASS_T_LEGS]:
            return 1
        return 0

    def process_frame(self):
        """
        Verarbeitet ein Frame
        """
        # Screenshot
        screenshot = self.sct.grab(self.monitor)
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        # Team-Erkennung (periodisch)
        current_time = time.time()
        if current_time - self.last_team_check > self.team_check_interval:
            detected_team = self.detect_player_team(frame)
            if detected_team != self.player_team:
                self.player_team = detected_team
                team_color = Fore.BLUE if detected_team == 'CT' else Fore.YELLOW
                print(f"{team_color}► Team: {detected_team}")
            self.last_team_check = current_time

        # Detection
        results = self.model.predict(
            frame,
            conf=self.confidence_threshold,
            verbose=False
        )[0]

        best_target = None
        best_priority = -1
        best_distance = float('inf')

        # Finde bestes Target
        if results.boxes is not None:
            for box in results.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                w = x2 - x1
                h = y2 - y1
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                # Distanz zum Crosshair
                dx = cx - self.screen_center[0]
                dy = cy - self.screen_center[1]
                distance = np.sqrt(dx**2 + dy**2)

                # FOV Check
                if distance > self.fov_radius:
                    continue

                # Team Check
                if not self.is_valid_target(class_id, frame, (x1, y1, w, h)):
                    continue

                # Priorität
                priority = self.get_target_priority(class_id)

                # Bestes Target wählen (Priorität > Distanz)
                if priority > best_priority or (priority == best_priority and distance < best_distance):
                    best_target = (cx, cy, class_id, confidence)
                    best_priority = priority
                    best_distance = distance

        return frame, best_target

    def aim_at_target(self, target):
        """
        Zielt auf Target mit smooth movement
        """
        if target is None:
            return

        tx, ty, class_id, confidence = target

        # Offset berechnen
        dx = tx - self.screen_center[0]
        dy = ty - self.screen_center[1]

        # Smooth Movement
        move_x = int(dx * self.smooth_factor)
        move_y = int(dy * self.smooth_factor)

        if abs(move_x) > 1 or abs(move_y) > 1:
            pyautogui.moveRel(move_x, move_y, duration=0.05)

    def run(self):
        """
        Hauptloop
        """
        print(f"{Fore.GREEN}Auto-Aim gestartet!")
        print(f"{Fore.YELLOW}Halte SHIFT zum Aktivieren...\n")

        try:
            while True:
                # SHIFT Check (0x10 = SHIFT key in Windows)
                import ctypes
                shift_pressed = ctypes.windll.user32.GetAsyncKeyState(0x10) & 0x8000

                if shift_pressed:
                    frame, target = self.process_frame()

                    if target:
                        self.aim_at_target(target)

                # Q zum Beenden
                if ctypes.windll.user32.GetAsyncKeyState(0x51) & 0x8000:  # Q key
                    break

                time.sleep(0.001)  # ~1000 FPS check rate

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Beendet.")

        print(f"{Fore.GREEN}Auto-Aim gestoppt.")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(f"{Fore.RED}Usage: python auto_aim_6class.py <model_path>")
        print(f"{Fore.YELLOW}Beispiel: python auto_aim_6class.py ../data/yolo_6class/runs/detect/train/weights/best.pt")
        sys.exit(1)

    model_path = sys.argv[1]

    if not os.path.exists(model_path):
        print(f"{Fore.RED}Model nicht gefunden: {model_path}")
        sys.exit(1)

    try:
        aim_bot = SixClassAutoAim(model_path)
        aim_bot.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Beendet.")
