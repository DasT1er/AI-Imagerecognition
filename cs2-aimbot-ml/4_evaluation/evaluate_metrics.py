"""
Metrics Evaluation Tool
=======================
Berechnet Accuracy, Precision, Recall und mAP auf dem Validation-Set.
"""

from ultralytics import YOLO
import os
from colorama import Fore, init

init(autoreset=True)

class MetricsEvaluator:
    def __init__(self, model_path, data_yaml):
        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.CYAN}CS2 6-Class Detection - Metrics Evaluation")
        print(f"{Fore.GREEN}{'='*70}\n")

        # Model laden
        print(f"{Fore.CYAN}Lade Model: {Fore.WHITE}{model_path}")
        self.model = YOLO(model_path)
        print(f"{Fore.GREEN}✓ Model geladen!\n")

        self.data_yaml = data_yaml

        # Klassen
        self.CLASS_NAMES = {
            0: "CT Body",
            1: "CT Head",
            2: "CT Legs",
            3: "T Body",
            4: "T Head",
            5: "T Legs"
        }

    def evaluate(self):
        """Führt Evaluation durch"""
        print(f"{Fore.YELLOW}Starte Evaluation auf Validation-Set...")
        print(f"{Fore.WHITE}Data: {Fore.CYAN}{self.data_yaml}\n")
        print(f"{Fore.YELLOW}Dies kann einige Minuten dauern...\n")

        # Validation durchführen
        results = self.model.val(
            data=self.data_yaml,
            split='val',
            save_json=True,
            plots=True
        )

        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"{Fore.GREEN}Evaluation abgeschlossen!")
        print(f"{Fore.GREEN}{'='*70}\n")

        # Ergebnisse anzeigen
        print(f"{Fore.CYAN}Gesamt-Metriken:")
        print(f"{Fore.WHITE}  mAP@50:    {Fore.GREEN}{results.box.map50:.3f}")
        print(f"{Fore.WHITE}  mAP@50-95: {Fore.GREEN}{results.box.map:.3f}")
        print(f"{Fore.WHITE}  Precision: {Fore.GREEN}{results.box.mp:.3f}")
        print(f"{Fore.WHITE}  Recall:    {Fore.GREEN}{results.box.mr:.3f}")

        # Pro-Klasse Metriken
        if hasattr(results.box, 'maps') and results.box.maps is not None:
            print(f"\n{Fore.CYAN}Pro-Klasse mAP@50:")

            # CT Team
            print(f"\n{Fore.BLUE}CT Team:")
            for i in range(3):
                if i < len(results.box.maps):
                    map_val = results.box.maps[i]
                    print(f"  {self.CLASS_NAMES[i]:12} {Fore.GREEN}{map_val:.3f}")

            # T Team
            print(f"\n{Fore.YELLOW}T Team:")
            for i in range(3, 6):
                if i < len(results.box.maps):
                    map_val = results.box.maps[i]
                    print(f"  {self.CLASS_NAMES[i]:12} {Fore.GREEN}{map_val:.3f}")

        print(f"\n{Fore.YELLOW}Interpretation:")
        print(f"  mAP@50 > 0.7  = {Fore.GREEN}Gut")
        print(f"  mAP@50 > 0.5  = {Fore.YELLOW}Okay")
        print(f"  mAP@50 < 0.5  = {Fore.RED}Mehr Training-Daten nötig")

        print(f"\n{Fore.CYAN}Visualisierungen gespeichert in:")
        print(f"  {Fore.WHITE}runs/detect/val/")
        print(f"  Siehe: confusion_matrix.png, val_batch_labels.jpg")

        print(f"\n{Fore.GREEN}{'='*70}\n")

        return results

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(f"{Fore.RED}Usage: python evaluate_metrics.py <model_path>")
        print(f"{Fore.YELLOW}Beispiel: python evaluate_metrics.py ../data/yolo_6class/runs/detect/train/weights/best.pt")
        sys.exit(1)

    model_path = sys.argv[1]

    if not os.path.exists(model_path):
        print(f"{Fore.RED}Model nicht gefunden: {model_path}")
        sys.exit(1)

    # Data YAML (anpassen falls nötig)
    data_yaml = "../data/yolo_6class/data.yaml"

    if not os.path.exists(data_yaml):
        print(f"{Fore.RED}data.yaml nicht gefunden: {data_yaml}")
        sys.exit(1)

    evaluator = MetricsEvaluator(model_path, data_yaml)
    evaluator.evaluate()
