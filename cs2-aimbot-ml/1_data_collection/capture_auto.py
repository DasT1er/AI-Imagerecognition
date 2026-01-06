"""
CS2 Auto-Screenshot Tool (Einfach!)
====================================
Macht AUTOMATISCH alle paar Sekunden Screenshots.
Kein Hotkey nötig - läuft einfach im Hintergrund!

Verwendung:
1. Starte dieses Script
2. Starte CS2
3. Spiele einfach normal!
4. Screenshots werden automatisch gemacht
5. Drücke CTRL+C im Terminal zum Beenden
"""

import mss
from PIL import Image
import time
import os
from datetime import datetime
from colorama import Fore, init

init(autoreset=True)

class AutoScreenshot:
    def __init__(self,
                 output_dir="../data/raw",
                 interval_seconds=2.0):  # Alle 2 Sekunden
        """
        Auto-Screenshot Tool

        Args:
            output_dir: Wo Screenshots gespeichert werden
            interval_seconds: Sekunden zwischen Screenshots
        """
        self.output_dir = output_dir
        self.interval = interval_seconds
        os.makedirs(output_dir, exist_ok=True)
        self.screenshot_count = 0
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]

        print(f"{Fore.GREEN}{'='*60}")
        print(f"{Fore.CYAN}CS2 Auto-Screenshot Tool")
        print(f"{Fore.GREEN}{'='*60}")
        print(f"{Fore.YELLOW}Einstellungen:")
        print(f"  Interval: {Fore.CYAN}{interval_seconds} Sekunden")
        print(f"  Ausgabe: {Fore.CYAN}{output_dir}")
        print(f"\n{Fore.WHITE}Macht automatisch alle {interval_seconds}s einen Screenshot!")
        print(f"{Fore.YELLOW}Drücke CTRL+C zum Beenden\n")
        print(f"{Fore.GREEN}{'='*60}\n")

    def capture_screenshot(self):
        """Macht einen Screenshot"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"cs2_screenshot_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)

        # Screenshot
        screenshot = self.sct.grab(self.monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
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
    capturer = AutoScreenshot(
        output_dir="../data/raw",
        interval_seconds=2.0    # Alle 2 Sekunden ein Screenshot
                                # Ändere auf 1.0 für schneller
                                # oder 3.0 für langsamer
    )
    capturer.run()
