"""
CS2 Real-time Target Detection
================================
Zeigt live was die AI erkennt während du CS2 spielst.

Features:
- Echtzeit-Detection mit Bounding Boxes
- FPS Counter
- Confidence Scores
- Optional: Overlay direkt im Spiel

Verwendung:
    python detect_realtime.py

Steuerung:
    Q - Beenden
"""

import cv2
import numpy as np
import mss
import time
from ultralytics import YOLO
from colorama import Fore, init
import os

init(autoreset=True)

class RealtimeDetector:
    def __init__(self, model_path="../models/cs2_target_detector_n/weights/best.pt",
                 confidence_threshold=0.5,
                 show_overlay=True):
        """
        CS2 Real-time Detector

        Args:
            model_path: Pfad zum trainierten Model
            confidence_threshold: Minimum Confidence für Detections
            show_overlay: Zeige Detection-Overlay
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.show_overlay = show_overlay

        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.CYAN}CS2 Real-time Target Detection")
        print(f"{Fore.GREEN}{'='*70}\n")

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
        self.monitor = self.sct.monitors[1]  # Hauptbildschirm

        # Stats
        self.fps = 0
        self.frame_times = []

        print(f"{Fore.WHITE}Konfiguration:")
        print(f"{Fore.WHITE}  Confidence Threshold: {Fore.CYAN}{confidence_threshold}")
        print(f"{Fore.WHITE}  Monitor: {Fore.CYAN}{self.monitor['width']}x{self.monitor['height']}")
        print(f"\n{Fore.YELLOW}Steuerung:")
        print(f"{Fore.WHITE}  Q - Beenden")
        print(f"{Fore.GREEN}{'='*70}\n")
        print(f"{Fore.CYAN}Detection läuft! Starte CS2...")

    def capture_screen(self):
        """Macht einen Screenshot"""
        screenshot = self.sct.grab(self.monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    def draw_detections(self, img, results):
        """Zeichnet Bounding Boxes und Labels auf das Bild"""
        overlay = img.copy()

        for result in results:
            boxes = result.boxes

            for box in boxes:
                # Confidence Check
                conf = float(box.conf[0])
                if conf < self.confidence_threshold:
                    continue

                # Box Koordinaten
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                # Farbe basierend auf Confidence (grün = gut, gelb = unsicher)
                if conf > 0.8:
                    color = (0, 255, 0)  # Grün
                elif conf > 0.6:
                    color = (0, 255, 255)  # Gelb
                else:
                    color = (0, 165, 255)  # Orange

                # Zeichne Box
                cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 3)

                # Label mit Confidence
                label = f"Enemy {conf:.2f}"
                label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)

                # Label Background
                cv2.rectangle(overlay,
                            (x1, y1 - label_size[1] - 10),
                            (x1 + label_size[0], y1),
                            color, -1)

                # Label Text
                cv2.putText(overlay, label, (x1, y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

                # Kreuz in der Mitte (Aim-Point)
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                cv2.drawMarker(overlay, (center_x, center_y),
                             color, cv2.MARKER_CROSS, 20, 2)

        return overlay

    def run(self):
        """Hauptloop für Real-time Detection"""
        print(f"{Fore.GREEN}Detection aktiv!")

        frame_count = 0
        start_time = time.time()

        try:
            while True:
                loop_start = time.time()

                # Capture Screen
                screen = self.capture_screen()

                # Run Detection
                results = self.model(screen, verbose=False, conf=self.confidence_threshold)

                # Draw Detections
                if self.show_overlay:
                    display = self.draw_detections(screen, results)
                else:
                    display = screen

                # FPS Counter
                self.frame_times.append(time.time() - loop_start)
                if len(self.frame_times) > 30:
                    self.frame_times.pop(0)
                self.fps = 1.0 / (sum(self.frame_times) / len(self.frame_times))

                # Detections zählen
                num_detections = sum(len(r.boxes) for r in results)

                # Info Overlay
                info_y = 30
                cv2.putText(display, f"FPS: {self.fps:.1f}", (10, info_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                cv2.putText(display, f"Targets: {num_detections}", (10, info_y + 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                cv2.putText(display, "Press Q to quit", (10, info_y + 80),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                # Resize für bessere Performance (optional)
                scale = 0.7
                width = int(display.shape[1] * scale)
                height = int(display.shape[0] * scale)
                display_resized = cv2.resize(display, (width, height))

                # Zeige Bild
                cv2.imshow('CS2 Target Detection', display_resized)

                # Tastatur Check
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break

                frame_count += 1

                # Stats alle 60 Frames
                if frame_count % 60 == 0:
                    elapsed = time.time() - start_time
                    avg_fps = frame_count / elapsed
                    print(f"{Fore.CYAN}Stats: {Fore.WHITE}FPS: {avg_fps:.1f} | "
                          f"Targets: {num_detections} | "
                          f"Frames: {frame_count}")

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Beendet durch Benutzer")

        finally:
            cv2.destroyAllWindows()
            total_time = time.time() - start_time
            avg_fps = frame_count / total_time if total_time > 0 else 0

            print(f"\n{Fore.GREEN}{'='*70}")
            print(f"{Fore.CYAN}Session Statistiken:")
            print(f"{Fore.WHITE}  Frames verarbeitet: {Fore.CYAN}{frame_count}")
            print(f"{Fore.WHITE}  Durchschnitt FPS: {Fore.CYAN}{avg_fps:.1f}")
            print(f"{Fore.WHITE}  Laufzeit: {Fore.CYAN}{total_time:.1f}s")
            print(f"{Fore.GREEN}{'='*70}\n")

def main():
    """Main Function"""

    # Finde das beste Model automatisch
    model_path = "../models/cs2_target_detector_n/weights/best.pt"

    # Falls nicht gefunden, suche nach anderen Models
    if not os.path.exists(model_path):
        models_dir = "../models"
        if os.path.exists(models_dir):
            runs = [d for d in os.listdir(models_dir) if d.startswith("cs2_target_detector")]
            if runs:
                latest_run = sorted(runs)[-1]
                model_path = os.path.join(models_dir, latest_run, "weights", "best.pt")

    # Starte Detector
    detector = RealtimeDetector(
        model_path=model_path,
        confidence_threshold=0.5,  # Nur Detections mit >50% Confidence
        show_overlay=True
    )

    detector.run()

if __name__ == "__main__":
    main()
