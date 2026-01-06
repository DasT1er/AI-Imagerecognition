"""
Model Evaluation Script
========================
Testet das trainierte Model auf dem Validation Set und zeigt detaillierte Metriken.

Verwendung:
    python evaluate_model.py

Zeigt:
- Precision, Recall, mAP
- Confusion Matrix
- Beispiel-Detections
"""

from ultralytics import YOLO
import os
from colorama import Fore, init
import cv2
import random

init(autoreset=True)

def evaluate_model(model_path="../models/cs2_target_detector_n/weights/best.pt",
                   data_yaml="../data/data.yaml"):
    """
    Evaluiert das Model auf dem Validation Set

    Args:
        model_path: Pfad zum Model
        data_yaml: Pfad zur data.yaml
    """

    print(f"{Fore.GREEN}{'='*70}")
    print(f"{Fore.CYAN}CS2 Model Evaluation")
    print(f"{Fore.GREEN}{'='*70}\n")

    # Check Files
    if not os.path.exists(model_path):
        print(f"{Fore.RED}Model nicht gefunden: {model_path}")
        return

    if not os.path.exists(data_yaml):
        print(f"{Fore.RED}data.yaml nicht gefunden: {data_yaml}")
        return

    # Lade Model
    print(f"{Fore.YELLOW}Lade Model: {Fore.CYAN}{model_path}")
    model = YOLO(model_path)
    print(f"{Fore.GREEN}✓ Model geladen!\n")

    # Evaluation
    print(f"{Fore.YELLOW}Starte Evaluation auf Validation Set...")
    print(f"{Fore.CYAN}{'─'*70}\n")

    results = model.val(data=data_yaml, plots=True, save_json=True)

    # Ergebnisse
    print(f"\n{Fore.GREEN}{'='*70}")
    print(f"{Fore.GREEN}Evaluation Ergebnisse")
    print(f"{Fore.GREEN}{'='*70}\n")

    # Metriken
    metrics = results.results_dict

    print(f"{Fore.YELLOW}Performance-Metriken:")
    print(f"{Fore.GREEN}{'─'*70}")

    if 'metrics/precision(B)' in metrics:
        precision = metrics['metrics/precision(B)']
        print(f"{Fore.WHITE}Precision: {Fore.CYAN}{precision:.3f}")
        print(f"{Fore.WHITE}  → Von allen Detections, wie viele sind korrekt?")

    if 'metrics/recall(B)' in metrics:
        recall = metrics['metrics/recall(B)']
        print(f"\n{Fore.WHITE}Recall: {Fore.CYAN}{recall:.3f}")
        print(f"{Fore.WHITE}  → Von allen echten Targets, wie viele wurden gefunden?")

    if 'metrics/mAP50(B)' in metrics:
        map50 = metrics['metrics/mAP50(B)']
        print(f"\n{Fore.WHITE}mAP@50: {Fore.CYAN}{map50:.3f}")
        print(f"{Fore.WHITE}  → Gesamt-Performance (IoU >= 50%)")

    if 'metrics/mAP50-95(B)' in metrics:
        map50_95 = metrics['metrics/mAP50-95(B)']
        print(f"\n{Fore.WHITE}mAP@50-95: {Fore.CYAN}{map50_95:.3f}")
        print(f"{Fore.WHITE}  → Strenge Gesamt-Performance (IoU 50%-95%)")

    print(f"{Fore.GREEN}{'─'*70}\n")

    # Interpretation
    print(f"{Fore.YELLOW}Interpretation:")
    if 'metrics/mAP50(B)' in metrics:
        map50 = metrics['metrics/mAP50(B)']

        if map50 > 0.9:
            print(f"{Fore.GREEN}🎯 EXZELLENT! Dein Model ist sehr gut!")
            print(f"{Fore.WHITE}   Das Model erkennt Gegner sehr zuverlässig.")

        elif map50 > 0.7:
            print(f"{Fore.CYAN}✓ GUT! Solide Performance.")
            print(f"{Fore.WHITE}   Das Model funktioniert gut für die meisten Situationen.")
            print(f"{Fore.YELLOW}   Tipp: Mehr Daten könnten es noch verbessern.")

        elif map50 > 0.5:
            print(f"{Fore.YELLOW}⚠ OK, aber noch Verbesserungspotential.")
            print(f"{Fore.WHITE}   Empfehlungen:")
            print(f"{Fore.WHITE}   • Sammle mehr Training-Daten (Ziel: 500+)")
            print(f"{Fore.WHITE}   • Stelle sicher dass Labels korrekt sind")
            print(f"{Fore.WHITE}   • Trainiere länger (mehr Epochs)")

        else:
            print(f"{Fore.RED}✗ Model braucht mehr Training.")
            print(f"{Fore.WHITE}   Empfehlungen:")
            print(f"{Fore.WHITE}   • Sammle VIEL mehr Daten (min. 300+)")
            print(f"{Fore.WHITE}   • Überprüfe deine Labels (sind sie korrekt?)")
            print(f"{Fore.WHITE}   • Verwende ein größeres Model (yolov8s oder yolov8m)")
            print(f"{Fore.WHITE}   • Trainiere viel länger (200+ Epochs)")

    print(f"\n{Fore.GREEN}{'='*70}")

    # Zeige Beispiel-Predictions
    show_predictions(model, data_yaml)

def show_predictions(model, data_yaml):
    """Zeigt einige Beispiel-Predictions"""

    print(f"\n{Fore.YELLOW}Zeige Beispiel-Predictions...")

    # Lade einige Validation-Bilder
    import yaml
    with open(data_yaml, 'r') as f:
        data = yaml.safe_load(f)

    val_images_dir = os.path.join(data['path'], data['val'])

    if not os.path.exists(val_images_dir):
        print(f"{Fore.RED}Validation-Bilder nicht gefunden")
        return

    # Wähle zufällige Bilder
    image_files = [f for f in os.listdir(val_images_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

    if not image_files:
        print(f"{Fore.RED}Keine Validation-Bilder gefunden")
        return

    sample_images = random.sample(image_files, min(5, len(image_files)))

    print(f"{Fore.CYAN}Zeige {len(sample_images)} Beispiele...")
    print(f"{Fore.WHITE}Drücke eine beliebige Taste um zum nächsten Bild zu wechseln")
    print(f"{Fore.WHITE}Drücke Q zum Überspringen\n")

    for img_file in sample_images:
        img_path = os.path.join(val_images_dir, img_file)
        img = cv2.imread(img_path)

        # Prediction
        results = model(img)

        # Zeichne Results
        annotated = results[0].plot()

        # Resize für Display
        scale = 0.6
        width = int(annotated.shape[1] * scale)
        height = int(annotated.shape[0] * scale)
        display = cv2.resize(annotated, (width, height))

        cv2.imshow('Model Predictions', display)

        key = cv2.waitKey(0) & 0xFF
        if key == ord('q'):
            break

    cv2.destroyAllWindows()
    print(f"{Fore.GREEN}✓ Beispiele gezeigt")

if __name__ == "__main__":
    try:
        # Finde Model automatisch
        model_path = "../models/cs2_target_detector_n/weights/best.pt"

        if not os.path.exists(model_path):
            models_dir = "../models"
            if os.path.exists(models_dir):
                runs = [d for d in os.listdir(models_dir) if d.startswith("cs2_target_detector")]
                if runs:
                    latest_run = sorted(runs)[-1]
                    model_path = os.path.join(models_dir, latest_run, "weights", "best.pt")

        evaluate_model(model_path)

    except Exception as e:
        print(f"{Fore.RED}Fehler: {e}")
