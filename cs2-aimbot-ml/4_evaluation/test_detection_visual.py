"""
Visuelles Testing Tool für CS2 6-Class Detection
=================================================
Zeigt Detections auf Test-Bildern an, damit du sehen kannst wie gut das Model funktioniert.
"""

import cv2
import os
from ultralytics import YOLO
from colorama import Fore, init
import numpy as np

init(autoreset=True)

class VisualTester:
    def __init__(self, model_path, test_images_dir="../data/raw"):
        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.CYAN}CS2 6-Class Detection - Visuelles Testing")
        print(f"{Fore.GREEN}{'='*70}\n")

        # Model laden
        print(f"{Fore.CYAN}Lade Model: {Fore.WHITE}{model_path}")
        self.model = YOLO(model_path)
        print(f"{Fore.GREEN}✓ Model geladen!\n")

        self.test_images_dir = test_images_dir

        # Klassen
        self.CLASS_NAMES = {
            0: "CT Body",
            1: "CT Head",
            2: "CT Legs",
            3: "T Body",
            4: "T Head",
            5: "T Legs"
        }

        # Farben (BGR für OpenCV)
        self.COLORS = {
            0: (255, 150, 0),    # CT Body - Blau
            1: (0, 255, 0),      # CT Head - Grün
            2: (255, 0, 255),    # CT Legs - Magenta
            3: (0, 165, 255),    # T Body - Orange
            4: (0, 255, 255),    # T Head - Gelb
            5: (255, 0, 128)     # T Legs - Pink
        }

    def test_on_images(self, confidence=0.4, num_images=20):
        """Zeigt Detections auf Test-Bildern"""

        # Sammle Bilder
        image_files = [f for f in os.listdir(self.test_images_dir)
                       if f.endswith(('.png', '.jpg', '.jpeg'))]

        if not image_files:
            print(f"{Fore.RED}Keine Bilder gefunden in {self.test_images_dir}")
            return

        # Limitiere Anzahl
        image_files = image_files[:num_images]

        print(f"{Fore.YELLOW}Teste auf {len(image_files)} Bildern...")
        print(f"{Fore.WHITE}Confidence Threshold: {Fore.CYAN}{confidence}\n")
        print(f"{Fore.CYAN}Steuerung:")
        print(f"  SPACE = Nächstes Bild")
        print(f"  Q     = Beenden\n")
        print(f"{Fore.GREEN}{'='*70}\n")

        # Statistiken
        total_detections = {i: 0 for i in range(6)}

        for idx, img_file in enumerate(image_files):
            img_path = os.path.join(self.test_images_dir, img_file)
            img = cv2.imread(img_path)

            if img is None:
                continue

            print(f"{Fore.CYAN}[{idx+1}/{len(image_files)}] {Fore.WHITE}{img_file}")

            # Detection
            results = self.model.predict(
                img,
                conf=confidence,
                verbose=False
            )[0]

            # Zeichne Detections
            display_img = img.copy()
            detections_count = {i: 0 for i in range(6)}

            if results.boxes is not None:
                for box in results.boxes:
                    class_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    # Farbe
                    color = self.COLORS.get(class_id, (255, 255, 255))

                    # Box zeichnen
                    cv2.rectangle(display_img, (x1, y1), (x2, y2), color, 2)

                    # Label
                    label = f"{self.CLASS_NAMES[class_id]} {conf:.2f}"

                    # Label-Hintergrund
                    (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                    cv2.rectangle(display_img, (x1, y1 - label_h - 10), (x1 + label_w, y1), color, -1)

                    # Label-Text
                    cv2.putText(display_img, label, (x1, y1 - 5),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

                    # Center marker
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2
                    cv2.drawMarker(display_img, (cx, cy), color, cv2.MARKER_CROSS, 20, 2)

                    detections_count[class_id] += 1
                    total_detections[class_id] += 1

            # Info-Text oben
            info_y = 30
            cv2.putText(display_img, f"Image {idx+1}/{len(image_files)}", (10, info_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            # Statistik für dieses Bild
            stats_text = f"Detected: CT:{detections_count[0]}+{detections_count[1]}+{detections_count[2]}  T:{detections_count[3]}+{detections_count[4]}+{detections_count[5]}"
            cv2.putText(display_img, stats_text, (10, info_y + 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            # Terminal output
            print(f"  CT: Body={detections_count[0]}, Head={detections_count[1]}, Legs={detections_count[2]}")
            print(f"  T:  Body={detections_count[3]}, Head={detections_count[4]}, Legs={detections_count[5]}")
            print()

            # Zeige Bild
            cv2.imshow('Detection Test - SPACE=Next, Q=Quit', display_img)

            key = cv2.waitKey(0) & 0xFF
            if key == ord('q') or key == ord('Q'):
                break

        cv2.destroyAllWindows()

        # Gesamt-Statistik
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"{Fore.CYAN}Gesamt-Statistik über {len(image_files)} Bilder:")
        print(f"{Fore.GREEN}{'='*70}\n")

        print(f"{Fore.BLUE}CT Team:")
        print(f"  Body: {total_detections[0]}")
        print(f"  Head: {total_detections[1]}")
        print(f"  Legs: {total_detections[2]}")
        print(f"  Total: {total_detections[0] + total_detections[1] + total_detections[2]}")

        print(f"\n{Fore.YELLOW}T Team:")
        print(f"  Body: {total_detections[3]}")
        print(f"  Head: {total_detections[4]}")
        print(f"  Legs: {total_detections[5]}")
        print(f"  Total: {total_detections[3] + total_detections[4] + total_detections[5]}")

        total_all = sum(total_detections.values())
        print(f"\n{Fore.GREEN}Gesamt: {total_all} Detections")
        print(f"{Fore.GREEN}{'='*70}\n")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(f"{Fore.RED}Usage: python test_detection_visual.py <model_path>")
        print(f"{Fore.YELLOW}Beispiel: python test_detection_visual.py ../data/yolo_6class/runs/detect/train/weights/best.pt")
        sys.exit(1)

    model_path = sys.argv[1]

    if not os.path.exists(model_path):
        print(f"{Fore.RED}Model nicht gefunden: {model_path}")
        sys.exit(1)

    tester = VisualTester(model_path)
    tester.test_on_images(confidence=0.4, num_images=20)
