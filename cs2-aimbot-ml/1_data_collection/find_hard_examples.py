"""
Active Learning - Find Hard Examples
=====================================
Findet Bilder wo das Model UNSICHER ist.
Diese sind am wertvollsten zum Labeln!

Strategie:
- Bilder mit niedrigen Confidence Scores
- Bilder mit wenigen/keine Detections
- Bilder mit Missklassifikationen
→ Diese labeln bringt den größten Fortschritt!
"""

import cv2
import os
import numpy as np
from ultralytics import YOLO
from colorama import Fore, init
import shutil

init(autoreset=True)

class HardExampleFinder:
    def __init__(self, model_path, images_dir="../data/raw"):
        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.CYAN}Active Learning - Hard Example Finder")
        print(f"{Fore.GREEN}{'='*70}\n")

        print(f"{Fore.CYAN}Lade Model...")
        self.model = YOLO(model_path)
        print(f"{Fore.GREEN}✓ Model geladen!\n")

        self.images_dir = images_dir

        # Sammle alle Bilder
        self.image_files = [f for f in os.listdir(images_dir)
                           if f.endswith(('.png', '.jpg', '.jpeg'))]

        print(f"{Fore.YELLOW}Analysiere {len(self.image_files)} Bilder...")
        print(f"{Fore.WHITE}Suche nach wertvollen Trainings-Beispielen...\n")

    def analyze_images(self):
        """Analysiert alle Bilder und findet schwierige"""

        results_data = []

        for idx, img_file in enumerate(self.image_files):
            if idx % 50 == 0:
                print(f"{Fore.CYAN}[{idx}/{len(self.image_files)}]")

            img_path = os.path.join(self.images_dir, img_file)
            img = cv2.imread(img_path)

            if img is None:
                continue

            # Predict
            results = self.model.predict(img, conf=0.3, verbose=False)[0]

            # Metrics berechnen
            num_detections = len(results.boxes) if results.boxes is not None else 0

            avg_confidence = 0
            head_count = 0
            low_conf_count = 0

            if results.boxes is not None:
                confidences = []
                for box in results.boxes:
                    conf = float(box.conf[0])
                    class_id = int(box.cls[0])

                    confidences.append(conf)

                    # Count heads (class 1 = CT Head, 4 = T Head)
                    if class_id in [1, 4]:
                        head_count += 1

                    if conf < 0.5:
                        low_conf_count += 1

                avg_confidence = np.mean(confidences) if confidences else 0

            # Score: Wie "schwierig" ist dieses Bild?
            difficulty_score = 0

            # Wenige Detections = schwierig
            if num_detections == 0:
                difficulty_score += 100
            elif num_detections < 3:
                difficulty_score += 50

            # Niedrige Confidence = unsicher
            if avg_confidence < 0.4:
                difficulty_score += 50
            elif avg_confidence < 0.6:
                difficulty_score += 30

            # Keine Köpfe erkannt = wichtig!
            if head_count == 0:
                difficulty_score += 40

            # Viele Low-Confidence Detections
            if low_conf_count > 0:
                difficulty_score += low_conf_count * 20

            results_data.append({
                'filename': img_file,
                'num_detections': num_detections,
                'avg_confidence': avg_confidence,
                'head_count': head_count,
                'low_conf_count': low_conf_count,
                'difficulty_score': difficulty_score
            })

        # Sortiere nach Schwierigkeit
        results_data.sort(key=lambda x: x['difficulty_score'], reverse=True)

        return results_data

    def export_hard_examples(self, results_data, top_n=100):
        """Exportiert die schwierigsten Beispiele"""

        output_dir = "../data/hard_examples"
        os.makedirs(output_dir, exist_ok=True)

        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"{Fore.CYAN}Top {top_n} schwierigste Bilder:")
        print(f"{Fore.GREEN}{'='*70}\n")

        for idx, data in enumerate(results_data[:top_n]):
            if idx < 20:  # Zeige erste 20
                print(f"{Fore.YELLOW}[{idx+1}] {data['filename']}")
                print(f"  Detections: {data['num_detections']}")
                print(f"  Avg Conf: {data['avg_confidence']:.2f}")
                print(f"  Heads: {data['head_count']}")
                print(f"  Difficulty: {data['difficulty_score']}")
                print()

            # Kopiere zu hard_examples
            src = os.path.join(self.images_dir, data['filename'])
            dst = os.path.join(output_dir, data['filename'])
            shutil.copy(src, dst)

        print(f"{Fore.GREEN}✓ {top_n} schwierige Bilder kopiert nach:")
        print(f"{Fore.CYAN}{output_dir}")

        print(f"\n{Fore.YELLOW}💡 TIPP:")
        print(f"{Fore.WHITE}Diese Bilder zu labeln bringt den größten Fortschritt!")
        print(f"{Fore.WHITE}Starte Semi-Auto Labeling mit:")
        print(f"{Fore.CYAN}python label_semi_auto.py")

        # Erstelle Report
        report_path = os.path.join(output_dir, "REPORT.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("HARD EXAMPLES REPORT\n")
            f.write("=" * 70 + "\n\n")

            f.write(f"Analysierte Bilder: {len(results_data)}\n")
            f.write(f"Hard Examples: {top_n}\n\n")

            f.write("WARUM DIESE BILDER WICHTIG SIND:\n")
            f.write("-" * 70 + "\n")
            f.write("• Model ist unsicher (niedrige Confidence)\n")
            f.write("• Wenige/keine Detections (schwierige Szenen)\n")
            f.write("• Keine Köpfe erkannt (Head-Detection verbessern!)\n\n")

            f.write("TOP 50:\n")
            f.write("-" * 70 + "\n")
            for idx, data in enumerate(results_data[:50]):
                f.write(f"{idx+1}. {data['filename']}\n")
                f.write(f"   Score: {data['difficulty_score']}, ")
                f.write(f"Detections: {data['num_detections']}, ")
                f.write(f"Heads: {data['head_count']}, ")
                f.write(f"Conf: {data['avg_confidence']:.2f}\n\n")

        print(f"{Fore.GREEN}✓ Report gespeichert: {report_path}")
        print(f"{Fore.GREEN}{'='*70}\n")

if __name__ == "__main__":
    import sys

    model_path = "../models/cs2_target_detector_n/weights/best.pt"

    if len(sys.argv) > 1:
        model_path = sys.argv[1]

    if not os.path.exists(model_path):
        print(f"{Fore.RED}Model nicht gefunden: {model_path}")
        print(f"{Fore.YELLOW}Trainiere erst ein Model!")
        sys.exit(1)

    finder = HardExampleFinder(model_path)
    results = finder.analyze_images()
    finder.export_hard_examples(results, top_n=100)
