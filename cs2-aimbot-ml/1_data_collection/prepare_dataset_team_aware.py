"""
Dataset Preparation für Team-Aware Training
===========================================
4 Klassen:
- Class 0: enemy_ct (Counter-Terrorist)
- Class 1: enemy_t (Terrorist)
- Class 2: head
- Class 3: legs
"""

import os
import shutil
import random
from colorama import Fore, init

init(autoreset=True)

def prepare_dataset(labeled_dir="../data/labeled_team_aware",
                    output_dir="../data",
                    train_split=0.8):

    images_dir = os.path.join(labeled_dir, "images")
    labels_dir = os.path.join(labeled_dir, "labels")

    train_images = os.path.join(output_dir, "train", "images")
    train_labels = os.path.join(output_dir, "train", "labels")
    val_images = os.path.join(output_dir, "val", "images")
    val_labels = os.path.join(output_dir, "val", "labels")

    for path in [train_images, train_labels, val_images, val_labels]:
        os.makedirs(path, exist_ok=True)

    print(f"{Fore.GREEN}{'='*70}")
    print(f"{Fore.CYAN}CS2 Team-Aware Dataset Preparation")
    print(f"{Fore.GREEN}{'='*70}\n")

    image_files = [f for f in os.listdir(images_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

    if not image_files:
        print(f"{Fore.RED}Keine Bilder gefunden")
        return

    # Statistiken
    total_ct = 0
    total_t = 0
    total_heads = 0
    total_legs = 0

    for img_file in image_files:
        label_file = os.path.splitext(img_file)[0] + '.txt'
        label_path = os.path.join(labels_dir, label_file)

        if os.path.exists(label_path):
            with open(label_path, 'r') as f:
                for line in f:
                    class_id = int(line.split()[0])
                    if class_id == 0:
                        total_ct += 1
                    elif class_id == 1:
                        total_t += 1
                    elif class_id == 2:
                        total_heads += 1
                    elif class_id == 3:
                        total_legs += 1

    random.shuffle(image_files)
    split_idx = int(len(image_files) * train_split)

    train_files = image_files[:split_idx]
    val_files = image_files[split_idx:]

    print(f"{Fore.WHITE}Bilder: {Fore.CYAN}{len(image_files)}")
    print(f"{Fore.WHITE}Training: {Fore.CYAN}{len(train_files)}")
    print(f"{Fore.WHITE}Validation: {Fore.CYAN}{len(val_files)}")
    print(f"\n{Fore.YELLOW}Labels:")
    print(f"{Fore.BLUE}  • Enemy CT: {Fore.CYAN}{total_ct}")
    print(f"{Fore.YELLOW}  • Enemy T: {Fore.CYAN}{total_t}")
    print(f"{Fore.RED}  • Heads: {Fore.CYAN}{total_heads}")
    print(f"{Fore.MAGENTA}  • Legs: {Fore.CYAN}{total_legs}\n")

    # Kopiere Training
    for img_file in train_files:
        label_file = os.path.splitext(img_file)[0] + '.txt'

        shutil.copy2(os.path.join(images_dir, img_file),
                     os.path.join(train_images, img_file))

        src_label = os.path.join(labels_dir, label_file)
        if os.path.exists(src_label):
            shutil.copy2(src_label, os.path.join(train_labels, label_file))

    print(f"{Fore.GREEN}✓ Training-Daten kopiert")

    # Kopiere Validation
    for img_file in val_files:
        label_file = os.path.splitext(img_file)[0] + '.txt'

        shutil.copy2(os.path.join(images_dir, img_file),
                     os.path.join(val_images, img_file))

        src_label = os.path.join(labels_dir, label_file)
        if os.path.exists(src_label):
            shutil.copy2(src_label, os.path.join(val_labels, label_file))

    print(f"{Fore.GREEN}✓ Validation-Daten kopiert")

    # Erstelle data.yaml
    yaml_content = f"""# CS2 Team-Aware Multi-Class Dataset
path: {os.path.abspath(output_dir)}
train: train/images
val: val/images

# Classes
nc: 4
names: ['enemy_ct', 'enemy_t', 'head', 'legs']

# Class 0: enemy_ct - Counter-Terrorist (nur gegnerisch)
# Class 1: enemy_t - Terrorist (nur gegnerisch)
# Class 2: head - Kopf (präzises Aiming)
# Class 3: legs - Beine (für Wallbang/Movement-Prediction)
"""

    yaml_path = os.path.join(output_dir, "data.yaml")
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)

    print(f"{Fore.GREEN}✓ data.yaml erstellt\n")
    print(f"{Fore.GREEN}{'='*70}")
    print(f"{Fore.GREEN}Dataset fertig!")
    print(f"{Fore.CYAN}Nächster Schritt: Training")
    print(f"{Fore.GREEN}{'='*70}\n")

if __name__ == "__main__":
    prepare_dataset()
