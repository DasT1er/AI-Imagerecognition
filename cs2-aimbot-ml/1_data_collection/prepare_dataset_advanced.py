"""
Dataset Preparation für Multi-Class Training
=============================================
Bereitet Dataset mit ZWEI Klassen vor: Enemy + Head

Erstellt data.yaml mit:
- Class 0: enemy (ganzer Gegner)
- Class 1: head (nur Kopf)
"""

import os
import shutil
import random
from pathlib import Path
from colorama import Fore, init

init(autoreset=True)

def prepare_dataset(labeled_dir="../data/labeled_advanced",
                    output_dir="../data",
                    train_split=0.8):
    """
    Bereitet Multi-Class Dataset für YOLO Training vor
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

    print(f"{Fore.GREEN}{'='*70}")
    print(f"{Fore.CYAN}CS2 Multi-Class Dataset Preparation")
    print(f"{Fore.GREEN}{'='*70}\n")

    # Sammle alle Bilder
    image_files = [f for f in os.listdir(images_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

    if not image_files:
        print(f"{Fore.RED}Keine Bilder gefunden in {images_dir}")
        print(f"{Fore.YELLOW}Tipp: Führe zuerst label_advanced.py aus!")
        return

    # Statistiken sammeln
    total_enemies = 0
    total_heads = 0

    for img_file in image_files:
        label_file = os.path.splitext(img_file)[0] + '.txt'
        label_path = os.path.join(labels_dir, label_file)

        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                for line in f:
                    class_id = int(line.split()[0])
                    if class_id == 0:
                        total_enemies += 1
                    elif class_id == 1:
                        total_heads += 1

    # Mische und teile auf
    random.shuffle(image_files)
    split_idx = int(len(image_files) * train_split)

    train_files = image_files[:split_idx]
    val_files = image_files[split_idx:]

    print(f"{Fore.WHITE}Gefundene Bilder: {Fore.CYAN}{len(image_files)}")
    print(f"{Fore.WHITE}Training Set: {Fore.CYAN}{len(train_files)} ({train_split*100:.0f}%)")
    print(f"{Fore.WHITE}Validation Set: {Fore.CYAN}{len(val_files)} ({(1-train_split)*100:.0f}%)")
    print(f"\n{Fore.YELLOW}Labels gefunden:")
    print(f"{Fore.GREEN}  • Enemies (Ganze Gegner): {Fore.CYAN}{total_enemies}")
    print(f"{Fore.RED}  • Heads (Köpfe): {Fore.CYAN}{total_heads}")
    print(f"{Fore.WHITE}  • Total: {Fore.CYAN}{total_enemies + total_heads}\n")

    # Kopiere Training Files
    print(f"{Fore.YELLOW}Kopiere Training-Daten...")
    for img_file in train_files:
        label_file = os.path.splitext(img_file)[0] + '.txt'

        src_img = os.path.join(images_dir, img_file)
        dst_img = os.path.join(train_images, img_file)
        shutil.copy2(src_img, dst_img)

        src_label = os.path.join(labels_dir, label_file)
        if os.path.exists(src_label):
            dst_label = os.path.join(train_labels, label_file)
            shutil.copy2(src_label, dst_label)

    print(f"{Fore.GREEN}✓ Training-Daten kopiert")

    # Kopiere Validation Files
    print(f"{Fore.YELLOW}Kopiere Validation-Daten...")
    for img_file in val_files:
        label_file = os.path.splitext(img_file)[0] + '.txt'

        src_img = os.path.join(images_dir, img_file)
        dst_img = os.path.join(val_images, img_file)
        shutil.copy2(src_img, dst_img)

        src_label = os.path.join(labels_dir, label_file)
        if os.path.exists(src_label):
            dst_label = os.path.join(val_labels, label_file)
            shutil.copy2(src_label, dst_label)

    print(f"{Fore.GREEN}✓ Validation-Daten kopiert")

    # Erstelle data.yaml für Multi-Class YOLO
    yaml_content = f"""# CS2 Multi-Class Target Detection Dataset
path: {os.path.abspath(output_dir)}
train: train/images
val: val/images

# Classes
nc: 2  # number of classes
names: ['enemy', 'head']  # class names

# Class 0: enemy - Ganzer Gegner (für Detection)
# Class 1: head  - Nur Kopf (für präzises Aiming)
"""

    yaml_path = os.path.join(output_dir, "data.yaml")
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)

    print(f"{Fore.GREEN}✓ data.yaml erstellt: {Fore.CYAN}{yaml_path}")

    # Finale Ausgabe
    print(f"\n{Fore.GREEN}{'='*70}")
    print(f"{Fore.GREEN}Multi-Class Dataset vorbereitet!")
    print(f"{Fore.GREEN}{'='*70}")
    print(f"{Fore.WHITE}Ordnerstruktur:")
    print(f"{Fore.CYAN}  {output_dir}/")
    print(f"{Fore.CYAN}  ├── train/")
    print(f"{Fore.CYAN}  │   ├── images/ ({len(train_files)} Bilder)")
    print(f"{Fore.CYAN}  │   └── labels/")
    print(f"{Fore.CYAN}  ├── val/")
    print(f"{Fore.CYAN}  │   ├── images/ ({len(val_files)} Bilder)")
    print(f"{Fore.CYAN}  │   └── labels/")
    print(f"{Fore.CYAN}  └── data.yaml (2 Klassen)")

    print(f"\n{Fore.YELLOW}Klassen:")
    print(f"{Fore.GREEN}  [0] enemy {Fore.WHITE}- Ganzer Gegner (für Detection)")
    print(f"{Fore.RED}  [1] head  {Fore.WHITE}- Nur Kopf (für Headshots)")

    print(f"\n{Fore.GREEN}{'='*70}\n")
    print(f"{Fore.YELLOW}Nächster Schritt:")
    print(f"{Fore.WHITE}  cd ../2_training")
    print(f"{Fore.WHITE}  python train_model.py")
    print(f"\n{Fore.CYAN}Die AI lernt jetzt:")
    print(f"{Fore.GREEN}  ✓ Wo Gegner sind (ganze Box)")
    print(f"{Fore.RED}  ✓ Wo Köpfe sind (exakte Position)")
    print(f"{Fore.YELLOW}  → Perfekte Headshots! 🎯\n")

if __name__ == "__main__":
    prepare_dataset()
