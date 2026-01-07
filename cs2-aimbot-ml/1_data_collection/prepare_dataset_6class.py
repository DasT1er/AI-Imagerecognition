"""
Dataset Preparation für 6-Class System
=======================================
Bereitet gelabelte Daten für YOLO Training vor mit 6 Klassen:
- CT Body, CT Head, CT Legs
- T Body, T Head, T Legs
"""

import os
import shutil
import random
from pathlib import Path
from colorama import Fore, init

init(autoreset=True)

def prepare_dataset(labeled_dir="../data/labeled_6class", output_dir="../data/yolo_6class", train_split=0.8):
    """
    Bereitet Dataset für YOLO Training vor
    """
    print(f"{Fore.GREEN}{'='*70}")
    print(f"{Fore.CYAN}CS2 6-Class Dataset Preparation")
    print(f"{Fore.GREEN}{'='*70}\n")

    # Input
    images_dir = os.path.join(labeled_dir, "images")
    labels_dir = os.path.join(labeled_dir, "labels")

    if not os.path.exists(images_dir) or not os.path.exists(labels_dir):
        print(f"{Fore.RED}Error: Labeled data nicht gefunden!")
        print(f"{Fore.YELLOW}Bitte erst label_6_class.py ausführen")
        return

    # Output
    train_images = os.path.join(output_dir, "train", "images")
    train_labels = os.path.join(output_dir, "train", "labels")
    val_images = os.path.join(output_dir, "val", "images")
    val_labels = os.path.join(output_dir, "val", "labels")

    # Erstelle Directories
    for dir_path in [train_images, train_labels, val_images, val_labels]:
        os.makedirs(dir_path, exist_ok=True)

    # Sammle alle Bilder mit Labels
    image_files = []
    for img_file in os.listdir(images_dir):
        if img_file.endswith(('.png', '.jpg', '.jpeg')):
            label_file = os.path.splitext(img_file)[0] + '.txt'
            label_path = os.path.join(labels_dir, label_file)

            if os.path.exists(label_path):
                image_files.append(img_file)

    if not image_files:
        print(f"{Fore.RED}Keine gelabelten Bilder gefunden!")
        return

    # Shuffle
    random.shuffle(image_files)

    # Split
    split_idx = int(len(image_files) * train_split)
    train_files = image_files[:split_idx]
    val_files = image_files[split_idx:]

    print(f"{Fore.CYAN}Gefundene Bilder: {Fore.WHITE}{len(image_files)}")
    print(f"{Fore.GREEN}Training Set:     {Fore.WHITE}{len(train_files)}")
    print(f"{Fore.YELLOW}Validation Set:   {Fore.WHITE}{len(val_files)}\n")

    # Statistiken
    class_counts = {i: {'train': 0, 'val': 0} for i in range(6)}
    class_names = ['CT Body', 'CT Head', 'CT Legs', 'T Body', 'T Head', 'T Legs']

    # Copy Train
    print(f"{Fore.CYAN}Kopiere Training Daten...")
    for img_file in train_files:
        label_file = os.path.splitext(img_file)[0] + '.txt'

        shutil.copy(os.path.join(images_dir, img_file), os.path.join(train_images, img_file))
        shutil.copy(os.path.join(labels_dir, label_file), os.path.join(train_labels, label_file))

        # Count classes
        with open(os.path.join(labels_dir, label_file), 'r') as f:
            for line in f:
                class_id = int(line.split()[0])
                if 0 <= class_id < 6:
                    class_counts[class_id]['train'] += 1

    # Copy Val
    print(f"{Fore.CYAN}Kopiere Validation Daten...")
    for img_file in val_files:
        label_file = os.path.splitext(img_file)[0] + '.txt'

        shutil.copy(os.path.join(images_dir, img_file), os.path.join(val_images, img_file))
        shutil.copy(os.path.join(labels_dir, label_file), os.path.join(val_labels, label_file))

        # Count classes
        with open(os.path.join(labels_dir, label_file), 'r') as f:
            for line in f:
                class_id = int(line.split()[0])
                if 0 <= class_id < 6:
                    class_counts[class_id]['val'] += 1

    # YAML erstellen
    yaml_path = os.path.join(output_dir, "data.yaml")
    yaml_content = f"""# CS2 6-Class Dataset (Vollständige Team-Separation)
path: {os.path.abspath(output_dir)}
train: train/images
val: val/images

# Classes (6 total)
nc: 6
names: ['ct_body', 'ct_head', 'ct_legs', 't_body', 't_head', 't_legs']

# Class Details:
# 0: ct_body - Counter-Terrorist Körper (ganzer Gegner)
# 1: ct_head - Counter-Terrorist Kopf (präzises Aiming)
# 2: ct_legs - Counter-Terrorist Beine (Movement Prediction)
# 3: t_body  - Terrorist Körper (ganzer Gegner)
# 4: t_head  - Terrorist Kopf (präzises Aiming)
# 5: t_legs  - Terrorist Beine (Movement Prediction)
"""

    with open(yaml_path, 'w') as f:
        f.write(yaml_content)

    print(f"{Fore.GREEN}\n✓ Dataset vorbereitet!")
    print(f"{Fore.CYAN}Output: {Fore.WHITE}{output_dir}\n")

    # Statistiken anzeigen
    print(f"{Fore.GREEN}{'='*70}")
    print(f"{Fore.CYAN}Klassen-Statistiken:")
    print(f"{Fore.GREEN}{'='*70}")

    print(f"\n{Fore.BLUE}CT Team:")
    for i in range(3):
        train_count = class_counts[i]['train']
        val_count = class_counts[i]['val']
        total = train_count + val_count
        print(f"  {class_names[i]:12} Train: {train_count:4}  Val: {val_count:4}  Total: {total:4}")

    print(f"\n{Fore.YELLOW}T Team:")
    for i in range(3, 6):
        train_count = class_counts[i]['train']
        val_count = class_counts[i]['val']
        total = train_count + val_count
        print(f"  {class_names[i]:12} Train: {train_count:4}  Val: {val_count:4}  Total: {total:4}")

    total_train = sum(class_counts[i]['train'] for i in range(6))
    total_val = sum(class_counts[i]['val'] for i in range(6))

    print(f"\n{Fore.GREEN}Gesamt:")
    print(f"  Train: {total_train}  Val: {total_val}  Total: {total_train + total_val}")

    print(f"\n{Fore.GREEN}{'='*70}")
    print(f"{Fore.CYAN}data.yaml erstellt:")
    print(f"{Fore.WHITE}{yaml_path}")
    print(f"{Fore.GREEN}{'='*70}\n")

    # Warnungen
    print(f"{Fore.YELLOW}Nächste Schritte:")
    print(f"  1. Prüfe Klassen-Balance (sollte ähnlich sein)")
    print(f"  2. Starte Training mit train_model.py")
    print(f"  3. Model Path: {output_dir}/data.yaml")

    # Balance Check
    print(f"\n{Fore.CYAN}Balance Check:")
    ct_total = sum(class_counts[i]['train'] + class_counts[i]['val'] for i in range(3))
    t_total = sum(class_counts[i]['train'] + class_counts[i]['val'] for i in range(3, 6))

    if ct_total > 0 and t_total > 0:
        ratio = ct_total / t_total if t_total > 0 else 0
        if 0.5 <= ratio <= 2.0:
            print(f"  {Fore.GREEN}✓ Teams gut balanciert (CT:{ct_total} / T:{t_total})")
        else:
            print(f"  {Fore.YELLOW}⚠ Teams unbalanciert (CT:{ct_total} / T:{t_total})")
            print(f"  {Fore.YELLOW}  Empfehlung: Mehr Daten vom unterrepräsentierten Team sammeln")

    # Head Check
    head_total = class_counts[1]['train'] + class_counts[1]['val'] + class_counts[4]['train'] + class_counts[4]['val']
    body_total = class_counts[0]['train'] + class_counts[0]['val'] + class_counts[3]['train'] + class_counts[3]['val']

    if head_total < body_total * 0.8:
        print(f"  {Fore.YELLOW}⚠ Wenige Head-Labels ({head_total} vs {body_total} Bodies)")
        print(f"  {Fore.YELLOW}  Empfehlung: Mehr Köpfe labeln für präzises Aiming")

    print()

if __name__ == "__main__":
    prepare_dataset()
