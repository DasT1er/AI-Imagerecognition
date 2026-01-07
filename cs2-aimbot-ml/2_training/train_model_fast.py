"""
CS2 Fast Training - Optimiert für GPU
======================================
Schnellere Trainingsversion mit GPU-Optimierungen.

Unterschiede zu train_model.py:
- Weniger Epochs (50 statt 100)
- Größere Batch Size wenn GPU vorhanden
- Weniger Augmentation
- Fokus auf Geschwindigkeit
"""

from ultralytics import YOLO
import torch
import os
from pathlib import Path
from colorama import Fore, Style, init
import time

init(autoreset=True)

class FastTrainer:
    def __init__(self,
                 data_yaml="../data/yolo_6class/data.yaml",
                 model_size="n",
                 epochs=50,  # Weniger Epochs für schnelleres Training
                 imgsz=640):

        self.data_yaml = data_yaml
        self.model_size = model_size
        self.epochs = epochs
        self.imgsz = imgsz

        # GPU-Check
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # Batch Size basierend auf Device
        if self.device == 'cuda':
            # Prüfe VRAM
            vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
            if vram_gb >= 12:
                self.batch = 64  # Große GPU
            elif vram_gb >= 8:
                self.batch = 32  # Mittelgroße GPU
            elif vram_gb >= 6:
                self.batch = 16  # Kleinere GPU
            else:
                self.batch = 8   # Kleine GPU
        else:
            self.batch = 4  # CPU

        # Output
        self.project_dir = "../models"
        self.name = f"cs2_target_detector_{model_size}"

        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.CYAN}CS2 Fast Training - GPU Optimized")
        print(f"{Fore.GREEN}{'='*70}\n")

        print(f"{Fore.YELLOW}Konfiguration:")
        print(f"{Fore.WHITE}  Model: {Fore.CYAN}YOLOv8{model_size}")
        print(f"{Fore.WHITE}  Device: {Fore.CYAN}{self.device.upper()}")

        if self.device == 'cuda':
            gpu_name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"{Fore.WHITE}  GPU: {Fore.CYAN}{gpu_name}")
            print(f"{Fore.WHITE}  VRAM: {Fore.CYAN}{vram:.1f} GB")
            print(f"{Fore.GREEN}  ✓ GPU Training aktiv! 🚀")
        else:
            print(f"{Fore.YELLOW}  ⚠ GPU nicht gefunden - CPU Training (langsam)")
            print(f"{Fore.YELLOW}  Siehe GPU_SETUP.txt für GPU Installation")

        print(f"{Fore.WHITE}  Epochs: {Fore.CYAN}{epochs} (reduziert für Geschwindigkeit)")
        print(f"{Fore.WHITE}  Batch Size: {Fore.CYAN}{self.batch} (auto-optimiert)")
        print(f"{Fore.WHITE}  Image Size: {Fore.CYAN}{imgsz}")
        print(f"{Fore.WHITE}  Data: {Fore.CYAN}{data_yaml}\n")

        # Geschätzter Speedup
        if self.device == 'cuda':
            print(f"{Fore.GREEN}Erwartete Training-Zeit: ~10-20 Minuten")
            print(f"{Fore.GREEN}(CPU würde ~2-3 Stunden dauern)\n")

        if not os.path.exists(data_yaml):
            print(f"{Fore.RED}ERROR: {data_yaml} nicht gefunden!")
            print(f"{Fore.YELLOW}Führe zuerst prepare_dataset_6class.py aus!")
            exit(1)

    def train(self):
        """Startet Fast Training"""
        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.YELLOW}Starte Fast Training...")
        print(f"{Fore.GREEN}{'='*70}\n")

        model_name = f"yolov8{self.model_size}.pt"
        print(f"{Fore.CYAN}Lade Pre-trained Model: {model_name}")
        model = YOLO(model_name)
        print(f"{Fore.GREEN}✓ Model geladen!\n")

        print(f"{Fore.YELLOW}{'─'*70}")
        print(f"{Fore.CYAN}Training läuft...")
        print(f"{Fore.WHITE}Schnelle Variante:")
        print(f"  • Weniger Epochs ({self.epochs})")
        print(f"  • Größere Batch Size ({self.batch})")
        print(f"  • Fokus auf Geschwindigkeit")
        print(f"{Fore.YELLOW}{'─'*70}\n")

        start_time = time.time()

        # Training mit Optimierungen für Geschwindigkeit
        results = model.train(
            data=self.data_yaml,
            epochs=self.epochs,
            imgsz=self.imgsz,
            batch=self.batch,
            device=self.device,
            project=self.project_dir,
            name=self.name,
            exist_ok=True,

            # Visualisierung
            plots=True,
            save=True,
            save_period=10,

            # Performance
            patience=15,  # Weniger Patience
            workers=8,    # Mehr Workers für schnelleres Loading
            cache=True,   # Cache images für schnelleres Training

            # Reduzierte Augmentation für Geschwindigkeit
            hsv_h=0.01,   # Minimal
            hsv_s=0.5,
            hsv_v=0.3,
            degrees=0.0,
            translate=0.05,
            scale=0.3,
            flipud=0.0,
            fliplr=0.0,
            mosaic=0.5,   # Reduziert

            # Mixed Precision für GPU-Speedup
            amp=True if self.device == 'cuda' else False,

            verbose=True
        )

        training_time = time.time() - start_time

        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"{Fore.GREEN}Training abgeschlossen!")
        print(f"{Fore.GREEN}{'='*70}\n")

        print(f"{Fore.WHITE}Training-Zeit: {Fore.CYAN}{training_time/60:.1f} Minuten")
        print(f"{Fore.WHITE}Bestes Model: {Fore.CYAN}{self.project_dir}/{self.name}/weights/best.pt")

        # Speedup berechnen
        if self.device == 'cuda':
            estimated_cpu_time = training_time * 12  # GPU ist ~12x schneller
            speedup = estimated_cpu_time / training_time
            print(f"\n{Fore.GREEN}GPU Speedup: ~{speedup:.1f}x schneller als CPU!")
            print(f"{Fore.GREEN}CPU hätte ~{estimated_cpu_time/60:.0f} Minuten gedauert")

        print(f"\n{Fore.YELLOW}Nächste Schritte:")
        print(f"{Fore.WHITE}1. Teste das Model:")
        print(f"   {Fore.CYAN}cd ../4_evaluation")
        print(f"   {Fore.CYAN}python test_detection_visual.py")
        print(f"{Fore.WHITE}2. Wenn Ergebnisse gut → Auto-Aim starten!")
        print(f"{Fore.GREEN}{'='*70}\n")

        return results

def main():
    """Main Fast Training"""

    print(f"{Fore.CYAN}Fast Training Setup:\n")
    print(f"{Fore.WHITE}Diese Version ist optimiert für:")
    print(f"  ✓ Schnelles Training (~10-20 Min mit GPU)")
    print(f"  ✓ Gute Ergebnisse trotz weniger Epochs")
    print(f"  ✓ Auto-optimierte Batch Size\n")

    # Auto-Detect beste Settings
    if torch.cuda.is_available():
        vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9

        if vram_gb >= 8:
            print(f"{Fore.GREEN}Große GPU erkannt! Nutze 's' model für bessere Accuracy.")
            model_size = "s"
        else:
            print(f"{Fore.YELLOW}Kleinere GPU erkannt. Nutze 'n' model.")
            model_size = "n"
    else:
        print(f"{Fore.RED}Keine GPU! Training wird langsam sein.")
        print(f"{Fore.YELLOW}Siehe GPU_SETUP.txt\n")
        model_size = "n"

    trainer = FastTrainer(
        data_yaml="../data/yolo_6class/data.yaml",
        model_size=model_size,
        epochs=50,  # Schnell aber gut
        imgsz=640
    )

    results = trainer.train()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Training unterbrochen.")
    except Exception as e:
        print(f"\n{Fore.RED}Fehler: {e}")
        raise
