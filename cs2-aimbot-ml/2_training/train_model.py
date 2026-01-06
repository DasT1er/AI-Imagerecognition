"""
CS2 Target Detection Training Script
=====================================
Trainiert ein YOLOv8 Model zur Erkennung von Gegnern in CS2.

Features:
- Live Training-Visualisierung
- Automatisches Speichern des besten Models
- TensorBoard Integration
- Progress-Tracking

Verwendung:
    python train_model.py

Der Trainingsfortschritt wird live angezeigt und in TensorBoard geloggt.
"""

from ultralytics import YOLO
import torch
import os
from pathlib import Path
from colorama import Fore, Style, init
import time

init(autoreset=True)

class CS2Trainer:
    def __init__(self,
                 data_yaml="../data/data.yaml",
                 model_size="n",  # n, s, m, l, x (nano ist am schnellsten)
                 epochs=100,
                 imgsz=640,
                 batch=16):
        """
        CS2 Target Detection Trainer

        Args:
            data_yaml: Pfad zur data.yaml
            model_size: YOLOv8 Modellgröße (n=nano, s=small, m=medium, l=large, x=xlarge)
            epochs: Anzahl Training Epochs
            imgsz: Bildgröße für Training
            batch: Batch Size
        """
        self.data_yaml = data_yaml
        self.model_size = model_size
        self.epochs = epochs
        self.imgsz = imgsz
        self.batch = batch

        # Output-Ordner
        self.project_dir = "../models"
        self.name = f"cs2_target_detector_{model_size}"

        # GPU Check
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.CYAN}CS2 Target Detection - Training")
        print(f"{Fore.GREEN}{'='*70}\n")

        print(f"{Fore.YELLOW}Konfiguration:")
        print(f"{Fore.WHITE}  Model: {Fore.CYAN}YOLOv8{model_size}")
        print(f"{Fore.WHITE}  Device: {Fore.CYAN}{self.device.upper()}")
        if self.device == 'cuda':
            print(f"{Fore.WHITE}  GPU: {Fore.CYAN}{torch.cuda.get_device_name(0)}")
        print(f"{Fore.WHITE}  Epochs: {Fore.CYAN}{epochs}")
        print(f"{Fore.WHITE}  Image Size: {Fore.CYAN}{imgsz}")
        print(f"{Fore.WHITE}  Batch Size: {Fore.CYAN}{batch}")
        print(f"{Fore.WHITE}  Data: {Fore.CYAN}{data_yaml}\n")

        # Check ob data.yaml existiert
        if not os.path.exists(data_yaml):
            print(f"{Fore.RED}ERROR: {data_yaml} nicht gefunden!")
            print(f"{Fore.YELLOW}Tipp: Führe zuerst prepare_dataset.py aus!")
            exit(1)

    def train(self):
        """Startet das Training"""
        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.YELLOW}Starte Training...")
        print(f"{Fore.GREEN}{'='*70}\n")

        # Lade YOLOv8 Model
        model_name = f"yolov8{self.model_size}.pt"
        print(f"{Fore.CYAN}Lade Pre-trained Model: {model_name}")
        model = YOLO(model_name)

        print(f"{Fore.GREEN}✓ Model geladen!\n")

        # Info-Text
        print(f"{Fore.YELLOW}{'─'*70}")
        print(f"{Fore.CYAN}Training läuft jetzt!")
        print(f"{Fore.WHITE}Du siehst:")
        print(f"  • Loss-Werte (sollten sinken)")
        print(f"  • mAP-Werte (sollten steigen)")
        print(f"  • Precision & Recall")
        print(f"\n{Fore.WHITE}Für detaillierte Visualisierung:")
        print(f"  {Fore.CYAN}tensorboard --logdir {self.project_dir}/{self.name}")
        print(f"{Fore.YELLOW}{'─'*70}\n")

        start_time = time.time()

        # Training starten
        results = model.train(
            data=self.data_yaml,
            epochs=self.epochs,
            imgsz=self.imgsz,
            batch=self.batch,
            device=self.device,
            project=self.project_dir,
            name=self.name,
            exist_ok=True,

            # Visualisierung & Logging
            plots=True,        # Training Plots erstellen
            save=True,         # Checkpoints speichern
            save_period=10,    # Alle 10 Epochs speichern

            # Performance
            patience=20,       # Early stopping nach 20 Epochs ohne Verbesserung

            # Augmentation (macht Model robuster)
            hsv_h=0.015,
            hsv_s=0.7,
            hsv_v=0.4,
            degrees=0.0,       # Keine Rotation (CS2 ist immer aufrecht)
            translate=0.1,
            scale=0.5,
            flipud=0.0,        # Kein vertikales Flip
            fliplr=0.0,        # Kein horizontales Flip (Waffen wären auf falscher Seite)
            mosaic=1.0,

            # Ausgabe
            verbose=True
        )

        training_time = time.time() - start_time

        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"{Fore.GREEN}Training abgeschlossen!")
        print(f"{Fore.GREEN}{'='*70}\n")

        print(f"{Fore.WHITE}Training-Zeit: {Fore.CYAN}{training_time/60:.1f} Minuten")
        print(f"{Fore.WHITE}Bestes Model: {Fore.CYAN}{self.project_dir}/{self.name}/weights/best.pt")
        print(f"{Fore.WHITE}Letztes Model: {Fore.CYAN}{self.project_dir}/{self.name}/weights/last.pt\n")

        # Ergebnisse
        print(f"{Fore.YELLOW}Training-Ergebnisse:")
        metrics = results.results_dict

        if 'metrics/mAP50(B)' in metrics:
            map50 = metrics['metrics/mAP50(B)']
            print(f"{Fore.WHITE}  mAP@50: {Fore.CYAN}{map50:.3f}")

        if 'metrics/mAP50-95(B)' in metrics:
            map50_95 = metrics['metrics/mAP50-95(B)']
            print(f"{Fore.WHITE}  mAP@50-95: {Fore.CYAN}{map50_95:.3f}")

        print(f"\n{Fore.YELLOW}Nächste Schritte:")
        print(f"{Fore.WHITE}1. Visualisiere Training:")
        print(f"   {Fore.CYAN}tensorboard --logdir {self.project_dir}/{self.name}")
        print(f"{Fore.WHITE}2. Teste das Model:")
        print(f"   {Fore.CYAN}python ../3_detection/detect_realtime.py")
        print(f"{Fore.GREEN}{'='*70}\n")

        return results

def main():
    """Main Training Function"""

    # Konfiguration
    trainer = CS2Trainer(
        data_yaml="../data/data.yaml",
        model_size="n",      # 'n' für schnelles Training, 's' oder 'm' für bessere Accuracy
        epochs=100,          # Mehr Epochs = besser, aber länger
        imgsz=640,           # Standardgröße
        batch=16             # Kleiner wenn GPU Out-of-Memory
    )

    # Training starten
    results = trainer.train()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Training unterbrochen.")
    except Exception as e:
        print(f"\n{Fore.RED}Fehler beim Training: {e}")
        raise
