"""
CS2 Auto-Screenshot Tool - PyAutoGUI Version
=============================================
Alternative Screenshot-Methode mit PyAutoGUI

PyAutoGUI:
+ Gute Kompatibilität
+ Stabile Farbwiedergabe
+ Einfach zu verwenden
- Mittlere Geschwindigkeit

NUTZE DIES wenn MSS zu überbelichtete Screenshots macht!
"""

import pyautogui
import time
import os
from datetime import datetime
from colorama import Fore, init

init(autoreset=True)

class AutoScreenshotPyAutoGUI:
    def __init__(self, output_dir="../data/raw", interval_seconds=2.0):
        """
        Auto-Screenshot Tool mit PyAutoGUI

        Args:
            output_dir: Wo Screenshots gespeichert werden
            interval_seconds: Sekunden zwischen Screenshots
        """
        self.output_dir = output_dir
        self.interval = interval_seconds
        os.makedirs(output_dir, exist_ok=True)
        self.screenshot_count = 0

        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"{Fore.CYAN}CS2 Auto-Screenshot Tool - PyAutoGUI")
        print(f"{Fore.GREEN}{'='*60}")
        print(f"{Fore.YELLOW}Einstellungen:")
        print(f"  Methode: {Fore.CYAN}PyAutoGUI (stabile Farbwiedergabe)")
        print(f"  Interval: {Fore.CYAN}{interval_seconds} Sekunden")
        print(f"  Ausgabe: {Fore.CYAN}{output_dir}")
        print(f"\n{Fore.GREEN}Vorteile dieser Methode:")
        print(f"  • Gute Kompatibilitaet")
        print(f"  • Stabile Farben")
        print(f"  • Weniger Ueberbelichtung als MSS")
        print(f"\n{Fore.WHITE}Macht automatisch alle {interval_seconds}s einen Screenshot!")
        print(f"{Fore.YELLOW}Druecke STRG+C zum Beenden\n")
        print(f"{Fore.GREEN}{'='*60}\n")

    def capture_screenshot(self):
        """Macht einen Screenshot mit PyAutoGUI"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"cs2_screenshot_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)

        # Screenshot mit PyAutoGUI
        img = pyautogui.screenshot()
        img.save(filepath)

        self.screenshot_count += 1
        print(f"{Fore.GREEN}✓ Screenshot #{self.screenshot_count}: {Fore.CYAN}{filename}")

    def run(self):
        """Hauptloop"""
        print(f"{Fore.GREEN}Auto-Screenshot gestartet!")
        print(f"{Fore.CYAN}Spiele jetzt CS2 und das Tool macht automatisch Screenshots...\n")

        try:
            while True:
                self.capture_screenshot()
                time.sleep(self.interval)

        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Beendet!")
            print(f"{Fore.GREEN}Insgesamt {self.screenshot_count} Screenshots gesammelt!")
            print(f"{Fore.CYAN}Gespeichert in: {self.output_dir}\n")

if __name__ == "__main__":
    # EINSTELLUNGEN HIER ANPASSEN:
    capturer = AutoScreenshotPyAutoGUI(
        output_dir="../data/raw",
        interval_seconds=2.0    # Alle 2 Sekunden ein Screenshot
    )
    capturer.run()
