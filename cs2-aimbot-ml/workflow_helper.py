"""
CS2 AI Training - Workflow Helper
==================================
Interaktiver Guide der dich durch den gesamten Prozess führt.

Verwendung:
    python workflow_helper.py
"""

import os
from colorama import Fore, Style, init

init(autoreset=True)

def print_header(text):
    """Druckt einen formatierten Header"""
    print(f"\n{Fore.GREEN}{'='*70}")
    print(f"{Fore.CYAN}{text}")
    print(f"{Fore.GREEN}{'='*70}\n")

def print_step(number, title):
    """Druckt einen Schritt-Header"""
    print(f"\n{Fore.YELLOW}{'─'*70}")
    print(f"{Fore.CYAN}SCHRITT {number}: {title}")
    print(f"{Fore.YELLOW}{'─'*70}\n")

def check_files(directory, pattern, min_count=0):
    """Prüft ob genug Files vorhanden sind"""
    if not os.path.exists(directory):
        return 0

    files = [f for f in os.listdir(directory) if pattern in f]
    return len(files)

def main():
    """Hauptfunktion"""

    print_header("CS2 AI Target Detection - Workflow Guide")

    print(f"{Fore.WHITE}Dieser Guide führt dich durch den kompletten Prozess!")
    print(f"{Fore.WHITE}Folge einfach Schritt für Schritt.\n")

    # ===== SCHRITT 1: Setup =====
    print_step(1, "Setup & Installation")

    print(f"{Fore.WHITE}Führe aus:")
    print(f"{Fore.CYAN}  pip install -r requirements.txt\n")

    input(f"{Fore.YELLOW}Drücke Enter wenn Installation fertig ist...")

    # ===== SCHRITT 2: Screenshots =====
    print_step(2, "Screenshots sammeln")

    raw_dir = "data/raw"
    screenshot_count = check_files(raw_dir, ".png")

    print(f"{Fore.WHITE}Aktuell: {Fore.CYAN}{screenshot_count} Screenshots\n")

    print(f"{Fore.WHITE}Was zu tun ist:")
    print(f"{Fore.WHITE}1. Starte CS2 (Offline gegen Bots!)")
    print(f"{Fore.WHITE}2. Führe aus:")
    print(f"{Fore.CYAN}     cd 1_data_collection")
    print(f"{Fore.CYAN}     python capture_screenshots.py")
    print(f"{Fore.WHITE}3. Drücke F9 wenn Gegner sichtbar sind")
    print(f"{Fore.WHITE}4. Drücke ESC wenn fertig\n")

    print(f"{Fore.YELLOW}Empfehlung: Min. 300 Screenshots für gute Ergebnisse")

    if screenshot_count < 100:
        print(f"{Fore.RED}⚠ Du hast noch zu wenige Screenshots!")
        print(f"{Fore.YELLOW}  Sammle mindestens 100, besser 300+\n")
    elif screenshot_count < 300:
        print(f"{Fore.YELLOW}✓ OK, aber mehr wäre besser (Ziel: 300+)\n")
    else:
        print(f"{Fore.GREEN}✓ Sehr gut! Du hast genug Screenshots!\n")

    input(f"{Fore.YELLOW}Drücke Enter wenn Screenshots gesammelt sind...")

    # ===== SCHRITT 3: Labeling =====
    print_step(3, "Gegner markieren (Labeling)")

    labeled_images = check_files("data/labeled/images", ".png")
    labeled_labels = check_files("data/labeled/labels", ".txt")

    print(f"{Fore.WHITE}Aktuell: {Fore.CYAN}{labeled_images} gelabelte Bilder\n")

    print(f"{Fore.WHITE}Was zu tun ist:")
    print(f"{Fore.WHITE}1. Führe aus:")
    print(f"{Fore.CYAN}     python label_targets.py")
    print(f"{Fore.WHITE}2. Ziehe Boxen um JEDEN Gegner")
    print(f"{Fore.WHITE}3. Drücke 's' zum Speichern")
    print(f"{Fore.WHITE}4. Drücke 'd' zum Überspringen\n")

    if labeled_images == 0:
        print(f"{Fore.RED}⚠ Noch keine Labels erstellt!")
        print(f"{Fore.YELLOW}  Starte das Labeling jetzt!\n")
    elif labeled_images < screenshot_count * 0.5:
        print(f"{Fore.YELLOW}⚠ Du hast erst {labeled_images}/{screenshot_count} gelabelt")
        print(f"{Fore.YELLOW}  Mach weiter mit dem Labeling!\n")
    else:
        print(f"{Fore.GREEN}✓ Gut! {labeled_images} Bilder gelabelt!\n")

    input(f"{Fore.YELLOW}Drücke Enter wenn Labeling fertig ist...")

    # ===== SCHRITT 4: Dataset Prep =====
    print_step(4, "Dataset vorbereiten")

    train_images = check_files("data/train/images", ".png")
    val_images = check_files("data/val/images", ".png")

    print(f"{Fore.WHITE}Aktuell:")
    print(f"{Fore.CYAN}  Training: {train_images} Bilder")
    print(f"{Fore.CYAN}  Validation: {val_images} Bilder\n")

    print(f"{Fore.WHITE}Was zu tun ist:")
    print(f"{Fore.WHITE}Führe aus:")
    print(f"{Fore.CYAN}  python prepare_dataset.py\n")

    if train_images == 0:
        print(f"{Fore.RED}⚠ Dataset noch nicht vorbereitet!")
        print(f"{Fore.YELLOW}  Führe prepare_dataset.py aus!\n")
    else:
        print(f"{Fore.GREEN}✓ Dataset ist vorbereitet!\n")

    input(f"{Fore.YELLOW}Drücke Enter wenn Dataset vorbereitet ist...")

    # ===== SCHRITT 5: Training =====
    print_step(5, "Model trainieren")

    model_exists = os.path.exists("models/cs2_target_detector_n/weights/best.pt")

    print(f"{Fore.WHITE}Was zu tun ist:")
    print(f"{Fore.WHITE}1. Führe aus:")
    print(f"{Fore.CYAN}     cd 2_training")
    print(f"{Fore.CYAN}     python train_model.py")
    print(f"{Fore.WHITE}2. Warte bis Training fertig ist (30 Min - 2 Stunden)")
    print(f"{Fore.WHITE}3. Beobachte wie Loss sinkt und mAP steigt!\n")

    print(f"{Fore.YELLOW}Optional: Live-Visualisierung mit TensorBoard:")
    print(f"{Fore.CYAN}  tensorboard --logdir models/cs2_target_detector_n\n")

    if not model_exists:
        print(f"{Fore.RED}⚠ Noch kein trainiertes Model!")
        print(f"{Fore.YELLOW}  Starte das Training jetzt!\n")
    else:
        print(f"{Fore.GREEN}✓ Model existiert bereits!\n")

    input(f"{Fore.YELLOW}Drücke Enter wenn Training fertig ist...")

    # ===== SCHRITT 6: Evaluation =====
    print_step(6, "Model evaluieren")

    print(f"{Fore.WHITE}Was zu tun ist:")
    print(f"{Fore.WHITE}1. Führe aus:")
    print(f"{Fore.CYAN}     cd 4_evaluation")
    print(f"{Fore.CYAN}     python evaluate_model.py")
    print(f"{Fore.WHITE}2. Sieh dir die Metriken an\n")

    print(f"{Fore.YELLOW}Interpretation:")
    print(f"{Fore.WHITE}  mAP@50 > 0.7 = Gut")
    print(f"{Fore.WHITE}  mAP@50 > 0.9 = Exzellent\n")

    input(f"{Fore.YELLOW}Drücke Enter um fortzufahren...")

    # ===== SCHRITT 7: Live-Test =====
    print_step(7, "Live-Test in CS2!")

    print(f"{Fore.WHITE}Was zu tun ist:")
    print(f"{Fore.WHITE}1. Führe aus:")
    print(f"{Fore.CYAN}     cd 3_detection")
    print(f"{Fore.CYAN}     python detect_realtime.py")
    print(f"{Fore.WHITE}2. Starte CS2 (Offline Bots)")
    print(f"{Fore.WHITE}3. Sieh die grünen Boxen um Gegner!")
    print(f"{Fore.WHITE}4. Drücke Q zum Beenden\n")

    input(f"{Fore.YELLOW}Drücke Enter um fortzufahren...")

    # ===== FERTIG! =====
    print_header("🎉 Workflow komplett!")

    print(f"{Fore.GREEN}Du hast alle Schritte durchlaufen!")
    print(f"\n{Fore.YELLOW}Nächste Schritte:")
    print(f"{Fore.WHITE}• Sammle mehr Daten für bessere Ergebnisse")
    print(f"{Fore.WHITE}• Trainiere länger (mehr Epochs)")
    print(f"{Fore.WHITE}• Experimentiere mit verschiedenen Settings")
    print(f"{Fore.WHITE}• Lies die README.md für erweiterte Optionen\n")

    print(f"{Fore.CYAN}Viel Spaß mit deiner AI! 🚀\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Guide beendet.")
