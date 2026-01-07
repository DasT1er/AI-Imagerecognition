"""
CS2 Auto-Screenshot Tool - PIL ImageGrab Version
=================================================
Alternative zu MSS mit besserer Farbgenauigkeit!

PIL ImageGrab:
+ Bessere Farbprofile (weniger Überbelichtung)
+ Verwendet Windows API direkt
+ Genauere Farben
- Etwas langsamer als MSS (aber immer noch schnell genug)

NUTZE DIES wenn MSS zu überbelichtete Screenshots macht!
"""

from PIL import ImageGrab
import time
import os
from datetime import datetime
from colorama import Fore, init

init(autoreset=True)

class AutoScreenshotPIL:
    def __init__(self, output_dir="../data/raw", interval_seconds=2.0):
        """
        Auto-Screenshot Tool mit PIL ImageGrab

        Args:
            output_dir: Wo Screenshots gespeichert werden
            interval_seconds: Sekunden zwischen Screenshots
        """
        self.output_dir = output_dir
        self.interval = interval_seconds
        os.makedirs(output_dir, exist_ok=True)
        self.screenshot_count = 0

        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"{Fore.CYAN}CS2 Auto-Screenshot Tool - PIL ImageGrab")
        print(f"{Fore.GREEN}{'='*60}")
        print(f"{Fore.YELLOW}Einstellungen:")
        print(f"  Methode: {Fore.CYAN}PIL ImageGrab (bessere Farbgenauigkeit)")
        print(f"  Interval: {Fore.CYAN}{interval_seconds} Sekunden")
        print(f"  Ausgabe: {Fore.CYAN}{output_dir}")
        print(f"\n{Fore.GREEN}Vorteile dieser Methode:")
        print(f"  • Bessere Farbprofile")
        print(f"  • Weniger Ueberbelichtung")
        print(f"  • Genauere Farben")
        print(f"\n{Fore.WHITE}Macht automatisch alle {interval_seconds}s einen Screenshot!")
        print(f"{Fore.YELLOW}Druecke STRG+C zum Beenden\n")
        print(f"{Fore.GREEN}{'='*60}\n")

    def capture_screenshot(self):
        """Macht einen Screenshot mit PIL ImageGrab"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"cs2_screenshot_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)

        # Screenshot mit PIL ImageGrab
        img = ImageGrab.grab(all_screens=False)
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
    capturer = AutoScreenshotPIL(
        output_dir="../data/raw",
        interval_seconds=2.0    # Alle 2 Sekunden ein Screenshot
    )
    capturer.run()
