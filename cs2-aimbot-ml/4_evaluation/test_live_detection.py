"""
Live Detection Test
===================
Zeigt Detections LIVE während du CS2 spielst - OHNE Aimbot!
Nur zum Testen wie gut die Erkennung funktioniert.
"""

import cv2
import numpy as np
import mss
import time
from ultralytics import YOLO
from colorama import Fore, init
import os

init(autoreset=True)

class LiveDetectionTester:
    def __init__(self, model_path):
        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.CYAN}CS2 Live Detection Test (ohne Aimbot)")
        print(f"{Fore.GREEN}{'='*70}\n")

        # Model laden
        print(f"{Fore.CYAN}Lade Model: {Fore.WHITE}{model_path}")
        self.model = YOLO(model_path)
        print(f"{Fore.GREEN}✓ Model geladen!\n")

        # Screenshot
        self.sct = mss.mss()
        self.monitor = self.select_monitor()

        # Config
        self.confidence = 0.4

        # Klassen
        self.CLASS_NAMES = {
            0: "CT Body",
            1: "CT Head",
            2: "CT Legs",
            3: "T Body",
            4: "T Head",
            5: "T Legs"
        }

        # Farben (BGR)
        self.COLORS = {
            0: (255, 150, 0),    # CT Body - Blau
            1: (0, 255, 0),      # CT Head - Grün
            2: (255, 0, 255),    # CT Legs - Magenta
            3: (0, 165, 255),    # T Body - Orange
            4: (0, 255, 255),    # T Head - Gelb
            5: (255, 0, 128)     # T Legs - Pink
        }

        # FPS
        self.fps = 0
        self.frame_times = []

        print(f"{Fore.YELLOW}Konfiguration:")
        print(f"  Confidence: {self.confidence}")
        print(f"  Monitor: {self.monitor['width']}x{self.monitor['height']}")
        print(f"\n{Fore.CYAN}Steuerung:")
        print(f"  Q = Beenden")
        print(f"\n{Fore.GREEN}Starte CS2 und spiele!")
        print(f"{Fore.YELLOW}Das Fenster zeigt was die AI sieht...\n")
        print(f"{Fore.GREEN}{'='*70}\n")

    def select_monitor(self):
        """Monitor auswählen"""
        monitors = self.sct.monitors

        print(f"{Fore.CYAN}Monitor-Auswahl:\n")

        for i in range(1, len(monitors)):
            mon = monitors[i]
            print(f"{Fore.CYAN}[{i}] {Fore.WHITE}Monitor {i} - {mon['width']}x{mon['height']}")

        while True:
            try:
                choice = input(f"{Fore.YELLOW}Wähle Monitor (1-{len(monitors)-1}): {Fore.WHITE}")
                monitor_num = int(choice)

                if 1 <= monitor_num < len(monitors):
                    selected = monitors[monitor_num]
                    print(f"{Fore.GREEN}✓ Monitor {monitor_num} gewählt!\n")
                    return selected
                else:
                    print(f"{Fore.RED}Ungültige Auswahl!")
            except ValueError:
                print(f"{Fore.RED}Bitte eine Zahl eingeben!")
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Abgebrochen.")
                exit(0)

    def run(self):
        """Hauptloop"""
        print(f"{Fore.GREEN}Live Detection gestartet!")

        while True:
            frame_start = time.time()

            # Screenshot
            screenshot = self.sct.grab(self.monitor)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            # Detection
            results = self.model.predict(
                frame,
                conf=self.confidence,
                verbose=False
            )[0]

            # Zeichne Detections
            display = frame.copy()
            detections_count = {i: 0 for i in range(6)}

            if results.boxes is not None:
                for box in results.boxes:
                    class_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    color = self.COLORS.get(class_id, (255, 255, 255))

                    # Box
                    cv2.rectangle(display, (x1, y1), (x2, y2), color, 2)

                    # Label
                    label = f"{self.CLASS_NAMES[class_id]} {conf:.2f}"
                    (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    cv2.rectangle(display, (x1, y1 - label_h - 8), (x1 + label_w, y1), color, -1)
                    cv2.putText(display, label, (x1, y1 - 5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

                    # Center
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2
                    cv2.drawMarker(display, (cx, cy), color, cv2.MARKER_CROSS, 15, 2)

                    detections_count[class_id] += 1

            # Info Overlay
            info_y = 30
            cv2.putText(display, f"FPS: {self.fps:.1f}", (10, info_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            ct_total = detections_count[0] + detections_count[1] + detections_count[2]
            t_total = detections_count[3] + detections_count[4] + detections_count[5]

            cv2.putText(display, f"CT: {ct_total}  T: {t_total}", (10, info_y + 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            # Resize für bessere Performance
            display_height = 720
            display_width = int(display.shape[1] * (display_height / display.shape[0]))
            display_resized = cv2.resize(display, (display_width, display_height))

            cv2.imshow('Live Detection Test - Q to Quit', display_resized)

            # FPS berechnen
            frame_time = time.time() - frame_start
            self.frame_times.append(frame_time)
            if len(self.frame_times) > 30:
                self.frame_times.pop(0)
            self.fps = 1.0 / (sum(self.frame_times) / len(self.frame_times))

            # Q zum Beenden
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()
        print(f"\n{Fore.GREEN}Live Detection beendet.")

if __name__ == "__main__":
    import sys

    # Standard-Pfad zum trainierten Model
    default_model_path = "../models/cs2_target_detector_n/weights/best.pt"

    if len(sys.argv) < 2:
        # Prüfe ob default model existiert
        if os.path.exists(default_model_path):
            print(f"{Fore.CYAN}Verwende Standard-Model: {default_model_path}\n")
            model_path = default_model_path
        else:
            print(f"{Fore.RED}Usage: python test_live_detection.py <model_path>")
            print(f"{Fore.YELLOW}Beispiel: python test_live_detection.py ../models/cs2_target_detector_n/weights/best.pt")
            print(f"\n{Fore.RED}Oder trainiere erst das Model mit:")
            print(f"{Fore.CYAN}cd ../2_training && python train_model.py")
            sys.exit(1)
    else:
        model_path = sys.argv[1]

    if not os.path.exists(model_path):
        print(f"{Fore.RED}Model nicht gefunden: {model_path}")
        sys.exit(1)

    try:
        tester = LiveDetectionTester(model_path)
        tester.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Beendet.")
