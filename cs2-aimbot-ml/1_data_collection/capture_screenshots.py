"""
CS2 Screenshot Capture Tool
============================
Einfaches Tool zum Sammeln von Screenshots während du CS2 spielst.

Verwendung:
1. Starte CS2 (am besten gegen Bots)
2. Starte dieses Script
3. Drücke F9 um Screenshots zu machen
4. Drücke ESC zum Beenden

Die Screenshots werden in data/raw/ gespeichert.
"""

import mss
import mss.tools
from PIL import Image
from pynput import keyboard
import time
import os
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

class ScreenshotCapture:
    def __init__(self, output_dir="../data/raw"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.screenshot_count = 0
        self.running = True
        self.sct = mss.mss()

        # Monitor auswählen (Hauptbildschirm)
        self.monitor = self.sct.monitors[1]

        print(f"{Fore.GREEN}{'='*60}")
        print(f"{Fore.CYAN}CS2 Screenshot Capture Tool")
        print(f"{Fore.GREEN}{'='*60}")
        print(f"{Fore.YELLOW}Steuerung:")
        print(f"  F9  - Screenshot machen")
        print(f"  ESC - Beenden")
        print(f"{Fore.GREEN}{'='*60}\n")
        print(f"{Fore.WHITE}Screenshots werden gespeichert in: {Fore.CYAN}{output_dir}")
        print(f"{Fore.WHITE}Bereit! Drücke F9 um Screenshots zu machen...\n")

    def capture_screenshot(self):
        """Macht einen Screenshot und speichert ihn"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"cs2_screenshot_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)

        # Screenshot machen
        screenshot = self.sct.grab(self.monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

        # Speichern
        img.save(filepath)
        self.screenshot_count += 1

        print(f"{Fore.GREEN}✓ Screenshot #{self.screenshot_count} gespeichert: {Fore.CYAN}{filename}")

    def on_press(self, key):
        """Tastendruck-Handler"""
        try:
            # F9 für Screenshot
            if key == keyboard.Key.f9:
                self.capture_screenshot()

            # ESC zum Beenden
            elif key == keyboard.Key.esc:
                print(f"\n{Fore.YELLOW}Beende...")
                print(f"{Fore.GREEN}Insgesamt {self.screenshot_count} Screenshots gesammelt!")
                self.running = False
                return False

        except AttributeError:
            pass

    def run(self):
        """Startet den Screenshot-Listener"""
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

if __name__ == "__main__":
    try:
        capture = ScreenshotCapture()
        capture.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Programm beendet.")
