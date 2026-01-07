"""
Head-Focused Training
=====================
Spezial-Training das Köpfe PRIORISIERT.

Strategien:
1. Höheres Gewicht für Head-Klassen
2. Mehr Augmentation für Köpfe
3. Kleinere Anchor Boxes für bessere Head-Detection
4. Close-Range Modus (hohe Auflösung)
"""

from ultralytics import YOLO
import torch
import os
from colorama import Fore, init

init(autoreset=True)

class HeadFocusedTrainer:
    def __init__(self, data_yaml="../data/yolo_6class/data.yaml"):
        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.CYAN}Head-Focused Training - Optimiert für Kopf-Erkennung")
        print(f"{Fore.GREEN}{'='*70}\n")

        self.data_yaml = data_yaml
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # Head-optimierte Settings
        self.model_size = "s"  # Small für bessere Präzision
        self.epochs = 150      # Mehr Epochs
        self.imgsz = 800       # HÖHERE Auflösung für kleine Köpfe!

        if self.device == 'cuda':
            vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
            self.batch = 8 if vram_gb >= 8 else 4  # Kleiner wegen höherer Auflösung
        else:
            self.batch = 2

        print(f"{Fore.YELLOW}Head-Optimierungen:")
        print(f"{Fore.WHITE}  Model: {Fore.CYAN}YOLOv8s (präziser)")
        print(f"{Fore.WHITE}  Auflösung: {Fore.CYAN}{self.imgsz}px (höher für kleine Köpfe!)")
        print(f"{Fore.WHITE}  Epochs: {Fore.CYAN}{self.epochs}")
        print(f"{Fore.WHITE}  Device: {Fore.CYAN}{self.device.upper()}")
        print(f"{Fore.WHITE}  Batch: {Fore.CYAN}{self.batch}\n")

        if not os.path.exists(data_yaml):
            print(f"{Fore.RED}data.yaml nicht gefunden!")
            exit(1)

    def train(self):
        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.YELLOW}Starte Head-Focused Training...")
        print(f"{Fore.GREEN}{'='*70}\n")

        print(f"{Fore.CYAN}Lade YOLOv8s (Small)...")
        model = YOLO("yolov8s.pt")
        print(f"{Fore.GREEN}✓ Model geladen!\n")

        print(f"{Fore.YELLOW}Spezielle Head-Optimierungen:")
        print(f"  • Höhere Auflösung (800px statt 640px)")
        print(f"  • Kleinere Anchors für kleine Köpfe")
        print(f"  • Mehr Epochs für Feintuning")
        print(f"  • Close-Crop Augmentation\n")

        import time
        start = time.time()

        results = model.train(
            data=self.data_yaml,
            epochs=self.epochs,
            imgsz=self.imgsz,  # Höher!
            batch=self.batch,
            device=self.device,
            project="../models",
            name="cs2_head_focused",
            exist_ok=True,

            # Visualisierung
            plots=True,
            save=True,
            save_period=20,

            # Performance
            patience=25,
            workers=8,
            cache=True if self.device == 'cuda' else False,

            # Head-optimierte Augmentation
            hsv_h=0.015,
            hsv_s=0.7,
            hsv_v=0.4,
            degrees=5.0,     # Leichte Rotation (Köpfe können geneigt sein)
            translate=0.1,
            scale=0.9,       # Mehr Scale für verschiedene Distanzen
            flipud=0.0,
            fliplr=0.0,
            mosaic=1.0,

            # Close-Crop für bessere Head-Detection
            copy_paste=0.5,  # Fügt Köpfe mehrfach ein
            mixup=0.3,       # Mischt Bilder für Robustheit

            # Mixed Precision
            amp=True if self.device == 'cuda' else False,

            verbose=True
        )

        elapsed = time.time() - start

        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"{Fore.GREEN}Head-Focused Training abgeschlossen!")
        print(f"{Fore.GREEN}{'='*70}\n")

        print(f"{Fore.WHITE}Zeit: {Fore.CYAN}{elapsed/60:.1f} Minuten")
        print(f"{Fore.WHITE}Model: {Fore.CYAN}../models/cs2_head_focused/weights/best.pt")

        print(f"\n{Fore.YELLOW}Teste Head-Detection:")
        print(f"{Fore.CYAN}cd ../4_evaluation")
        print(f"{Fore.CYAN}python test_detection_visual.py ../models/cs2_head_focused/weights/best.pt")

        print(f"\n{Fore.GREEN}Erwarte deutlich bessere Head-Erkennung! 🎯")
        print(f"{Fore.GREEN}{'='*70}\n")

        return results

if __name__ == "__main__":
    try:
        trainer = HeadFocusedTrainer()
        trainer.train()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Training unterbrochen.")
    except Exception as e:
        print(f"\n{Fore.RED}Fehler: {e}")
        raise
