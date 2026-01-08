"""
CS2 Auto-Screenshot Tool - PIL ImageGrab
=========================================
Nutzt die gleiche Methode wie Windows-Screenshots!

Wenn normale Windows-Screenshots gut aussehen,
aber DXCam überbelichtet ist → Nutze dies!
"""

from PIL import ImageGrab
import time
import os
from datetime import datetime
from colorama import Fore, init

init(autoreset=True)

class AutoScreenshot:
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
        print(f"  Methode: {Fore.CYAN}PIL ImageGrab (wie Windows-Screenshots)")
        print(f"  Interval: {Fore.CYAN}{interval_seconds} Sekunden")
        print(f"  Ausgabe: {Fore.CYAN}{output_dir}")
        print(f"\n{Fore.GREEN}Vorteile:")
        print(f"  • Gleiche Methode wie Windows-Screenshots")
        print(f"  • Funktioniert wenn normale Screenshots OK sind")
        print(f"  • Keine DXCam Color-Space Probleme")
        print(f"\n{Fore.WHITE}Macht automatisch alle {interval_seconds}s einen Screenshot!")
        print(f"{Fore.YELLOW}Druecke STRG+C zum Beenden\n")
        print(f"{Fore.GREEN}{'='*60}\n")

    def capture_screenshot(self):
        """Macht einen Screenshot mit PIL ImageGrab"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"cs2_screenshot_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)

        # Screenshot mit PIL ImageGrab (wie Windows!)
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
    capturer = AutoScreenshot(
        output_dir="../data/raw",
        interval_seconds=2.0
    )
    capturer.run()
