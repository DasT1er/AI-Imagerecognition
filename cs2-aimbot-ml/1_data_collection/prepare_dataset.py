"""
Dataset Preparation Script
===========================
Teilt die gelabelten Daten in Training und Validation Sets auf.

Train: 80%
Val: 20%

Erstellt auch die YOLO data.yaml Konfigurationsdatei.
"""

import os
import shutil
import random
from pathlib import Path
from colorama import Fore, init

init(autoreset=True)

def prepare_dataset(labeled_dir="../data/labeled",
                    output_dir="../data",
                    train_split=0.8):
    """
    Bereitet Dataset für YOLO Training vor

    Args:
        labeled_dir: Ordner mit gelabelten Bildern und Labels
        output_dir: Ausgabe-Ordner für train/val split
        train_split: Prozentsatz für Training (0.8 = 80%)
    """

    images_dir = os.path.join(labeled_dir, "images")
    labels_dir = os.path.join(labeled_dir, "labels")

    # Erstelle Ausgabe-Struktur
    train_images = os.path.join(output_dir, "train", "images")
    train_labels = os.path.join(output_dir, "train", "labels")
    val_images = os.path.join(output_dir, "val", "images")
    val_labels = os.path.join(output_dir, "val", "labels")

    for path in [train_images, train_labels, val_images, val_labels]:
        os.makedirs(path, exist_ok=True)

    print(f"{Fore.GREEN}{'='*60}")
    print(f"{Fore.CYAN}CS2 Dataset Preparation")
    print(f"{Fore.GREEN}{'='*60}\n")

    # Sammle alle Bilder
    image_files = [f for f in os.listdir(images_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

    if not image_files:
        print(f"{Fore.RED}Keine Bilder gefunden in {images_dir}")
        print(f"{Fore.YELLOW}Tipp: Führe zuerst label_targets.py aus!")
        return

    # Mische und teile auf
    random.shuffle(image_files)
    split_idx = int(len(image_files) * train_split)

    train_files = image_files[:split_idx]
    val_files = image_files[split_idx:]

    print(f"{Fore.WHITE}Gefundene Bilder: {Fore.CYAN}{len(image_files)}")
    print(f"{Fore.WHITE}Training Set: {Fore.CYAN}{len(train_files)} ({train_split*100:.0f}%)")
    print(f"{Fore.WHITE}Validation Set: {Fore.CYAN}{len(val_files)} ({(1-train_split)*100:.0f}%)\n")

    # Kopiere Training Files
    print(f"{Fore.YELLOW}Kopiere Training-Daten...")
    for img_file in train_files:
        label_file = os.path.splitext(img_file)[0] + '.txt'

        # Kopiere Bild
        src_img = os.path.join(images_dir, img_file)
        dst_img = os.path.join(train_images, img_file)
        shutil.copy2(src_img, dst_img)

        # Kopiere Label (falls vorhanden)
        src_label = os.path.join(labels_dir, label_file)
        if os.path.exists(src_label):
            dst_label = os.path.join(train_labels, label_file)
            shutil.copy2(src_label, dst_label)

    print(f"{Fore.GREEN}✓ Training-Daten kopiert")

    # Kopiere Validation Files
    print(f"{Fore.YELLOW}Kopiere Validation-Daten...")
    for img_file in val_files:
        label_file = os.path.splitext(img_file)[0] + '.txt'

        # Kopiere Bild
        src_img = os.path.join(images_dir, img_file)
        dst_img = os.path.join(val_images, img_file)
        shutil.copy2(src_img, dst_img)

        # Kopiere Label (falls vorhanden)
        src_label = os.path.join(labels_dir, label_file)
        if os.path.exists(src_label):
            dst_label = os.path.join(val_labels, label_file)
            shutil.copy2(src_label, dst_label)

    print(f"{Fore.GREEN}✓ Validation-Daten kopiert")

    # Erstelle data.yaml für YOLO
    yaml_content = f"""# CS2 Target Detection Dataset
path: {os.path.abspath(output_dir)}
train: train/images
val: val/images

# Classes
nc: 1  # number of classes
names: ['enemy']  # class names
"""

    yaml_path = os.path.join(output_dir, "data.yaml")
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)

    print(f"{Fore.GREEN}✓ data.yaml erstellt: {Fore.CYAN}{yaml_path}")

    # Statistiken
    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"{Fore.GREEN}Dataset-Vorbereitung abgeschlossen!")
    print(f"{Fore.GREEN}{'='*60}")
    print(f"{Fore.WHITE}Ordnerstruktur:")
    print(f"{Fore.CYAN}  {output_dir}/")
    print(f"{Fore.CYAN}  ├── train/")
    print(f"{Fore.CYAN}  │   ├── images/ ({len(train_files)} Bilder)")
    print(f"{Fore.CYAN}  │   └── labels/ ({len(train_files)} Labels)")
    print(f"{Fore.CYAN}  ├── val/")
    print(f"{Fore.CYAN}  │   ├── images/ ({len(val_files)} Bilder)")
    print(f"{Fore.CYAN}  │   └── labels/ ({len(val_files)} Labels)")
    print(f"{Fore.CYAN}  └── data.yaml")
    print(f"{Fore.GREEN}{'='*60}\n")
    print(f"{Fore.YELLOW}Nächster Schritt: Starte das Training mit train_model.py")

if __name__ == "__main__":
    prepare_dataset()
