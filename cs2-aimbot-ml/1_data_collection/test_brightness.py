"""
Brightness Test Tool
====================
Macht einen Screenshot und zeigt verschiedene Helligkeiten.
So kannst du sehen welche Einstellung am besten ist!
"""

import mss
from PIL import Image, ImageEnhance
import numpy as np
import cv2
from colorama import Fore, init

init(autoreset=True)

def select_monitor():
    """Monitor auswählen"""
    sct = mss.mss()
    monitors = sct.monitors

    print(f"{Fore.GREEN}{'='*60}")
    print(f"{Fore.CYAN}Monitor-Auswahl")
    print(f"{Fore.GREEN}{'='*60}\n")

    for i in range(1, len(monitors)):
        mon = monitors[i]
        print(f"{Fore.CYAN}[{i}] {Fore.WHITE}Monitor {i}: {mon['width']}x{mon['height']}")

    while True:
        try:
            choice = input(f"\n{Fore.YELLOW}Wähle Monitor (1-{len(monitors)-1}): {Fore.WHITE}")
            monitor_num = int(choice)
            if 1 <= monitor_num < len(monitors):
                return sct, monitors[monitor_num]
            else:
                print(f"{Fore.RED}Ungültige Auswahl!")
        except ValueError:
            print(f"{Fore.RED}Bitte eine Zahl eingeben!")

def apply_corrections(img, brightness, apply_gamma):
    """Wendet Korrekturen an"""
    # Gamma-Korrektur
    if apply_gamma:
        img_array = np.array(img).astype(np.float32) / 255.0
        gamma = 1.0 / 2.2
        img_array = np.power(img_array, gamma)
        img = Image.fromarray((img_array * 255).astype(np.uint8))

    # Helligkeit
    if brightness != 1.0:
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(brightness)

    return img

def main():
    print(f"{Fore.GREEN}{'='*60}")
    print(f"{Fore.CYAN}Brightness Test Tool")
    print(f"{Fore.GREEN}{'='*60}\n")

    sct, monitor = select_monitor()

    print(f"\n{Fore.YELLOW}Mache Test-Screenshot...")
    screenshot = sct.grab(monitor)
    original = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

    print(f"{Fore.GREEN}✓ Screenshot gemacht!\n")
    print(f"{Fore.CYAN}Zeige 6 verschiedene Einstellungen...\n")

    # Verschiedene Einstellungen testen
    tests = [
        ("Original", 1.0, False),
        ("Gamma Only", 1.0, True),
        ("85% + Gamma", 0.85, True),
        ("75% + Gamma", 0.75, True),
        ("90% + Gamma", 0.90, True),
        ("80% + Gamma", 0.80, True),
    ]

    # Erstelle Vergleichsbild
    results = []
    for name, brightness, gamma in tests:
        img = apply_corrections(original.copy(), brightness, gamma)
        # Resize für Anzeige
        img_resized = img.resize((640, 360))
        img_cv = cv2.cvtColor(np.array(img_resized), cv2.COLOR_RGB2BGR)

        # Label hinzufügen
        cv2.putText(img_cv, name, (10, 30),
                   cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(img_cv, f"Brightness: {brightness:.2f}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(img_cv, f"Gamma: {'Yes' if gamma else 'No'}", (10, 85),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        results.append(img_cv)

    # Kombiniere zu Grid (2x3)
    row1 = np.hstack([results[0], results[1], results[2]])
    row2 = np.hstack([results[3], results[4], results[5]])
    grid = np.vstack([row1, row2])

    print(f"{Fore.GREEN}{'='*60}")
    print(f"{Fore.CYAN}Vergleich wird angezeigt!")
    print(f"{Fore.GREEN}{'='*60}\n")
    print(f"{Fore.YELLOW}Empfehlung:")
    print(f"  • Wenn zu hell: Nutze '85% + Gamma' oder '80% + Gamma'")
    print(f"  • Wenn OK: Nutze 'Gamma Only' oder '90% + Gamma'")
    print(f"  • Wenn zu dunkel: Nutze 'Original'\n")
    print(f"{Fore.WHITE}Drücke eine beliebige Taste zum Beenden...\n")

    cv2.imshow('Brightness Test - Welche Einstellung ist am besten?', grid)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    print(f"\n{Fore.CYAN}Setze deine gewünschte Einstellung in capture_auto.py:")
    print(f"{Fore.WHITE}  brightness_correction=0.85  # Ändere diesen Wert")
    print(f"{Fore.WHITE}  apply_gamma_correction=True # True oder False\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Abgebrochen.")
