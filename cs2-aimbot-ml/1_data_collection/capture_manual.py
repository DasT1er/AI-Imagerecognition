"""
CS2 Manual Screenshot Tool (Funktioniert immer!)
================================================
Drücke einfach ENTER im Terminal für einen Screenshot.

Verwendung:
1. Starte dieses Script (Terminal bleibt offen)
2. Starte CS2
3. Wechsle ins Terminal und drücke ENTER für Screenshot
4. Tippe 'q' und drücke ENTER zum Beenden
"""

import mss
from PIL import Image
import os
from datetime import datetime
from colorama import Fore, init

init(autoreset=True)

class ManualScreenshot:
    def __init__(self, output_dir="../data/raw"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.screenshot_count = 0
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]

        print(f"{Fore.GREEN}{'='*60}")
        print(f"{Fore.CYAN}CS2 Manual Screenshot Tool")
        print(f"{Fore.GREEN}{'='*60}")
        print(f"{Fore.YELLOW}Steuerung:")
        print(f"  ENTER - Screenshot machen")
        print(f"  q + ENTER - Beenden")
        print(f"{Fore.GREEN}{'='*60}\n")
        print(f"{Fore.WHITE}Screenshots: {Fore.CYAN}{output_dir}\n")

    def capture_screenshot(self):
        """Macht einen Screenshot"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"cs2_screenshot_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)

        screenshot = self.sct.grab(self.monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        img.save(filepath)

        self.screenshot_count += 1
        print(f"{Fore.GREEN}✓ Screenshot #{self.screenshot_count} gespeichert!")

    def run(self):
        """Hauptloop"""
        print(f"{Fore.GREEN}Bereit!")
        print(f"{Fore.CYAN}Drücke ENTER für Screenshot, 'q' zum Beenden...\n")

        while True:
            user_input = input(f"{Fore.YELLOW}[{self.screenshot_count}] {Fore.WHITE}Drücke ENTER: ")

            if user_input.lower() == 'q':
                break

            self.capture_screenshot()

        print(f"\n{Fore.GREEN}Fertig! {self.screenshot_count} Screenshots gesammelt!\n")

if __name__ == "__main__":
    capturer = ManualScreenshot()
    capturer.run()
