"""
CS2 Auto-Screenshot Tool (Multi-Monitor Support!)
==================================================
Macht AUTOMATISCH alle paar Sekunden Screenshots.
Kein Hotkey nötig - läuft einfach im Hintergrund!

Verwendung:
1. Starte dieses Script
2. Wähle deinen Monitor aus
3. Starte CS2
4. Spiele einfach normal!
5. Screenshots werden automatisch gemacht
6. Drücke CTRL+C im Terminal zum Beenden
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

        # Monitor-Auswahl
        self.monitor = self.select_monitor()

        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"{Fore.CYAN}CS2 Auto-Screenshot Tool")
        print(f"{Fore.GREEN}{'='*60}")
        print(f"{Fore.YELLOW}Einstellungen:")
        print(f"  Monitor: {Fore.CYAN}{self.monitor['width']}x{self.monitor['height']}")
        print(f"  Interval: {Fore.CYAN}{interval_seconds} Sekunden")
        print(f"  Ausgabe: {Fore.CYAN}{output_dir}")
        print(f"\n{Fore.WHITE}Macht automatisch alle {interval_seconds}s einen Screenshot!")
        print(f"{Fore.YELLOW}Drücke CTRL+C zum Beenden\n")
        print(f"{Fore.GREEN}{'='*60}\n")

    def select_monitor(self):
        """Lässt User Monitor auswählen"""
        monitors = self.sct.monitors

        print(f"{Fore.GREEN}{'='*60}")
        print(f"{Fore.CYAN}Monitor-Auswahl")
        print(f"{Fore.GREEN}{'='*60}\n")

        print(f"{Fore.YELLOW}Verfügbare Monitore:\n")

        # Monitor 0 ist "All Monitors" - überspringen
        for i in range(1, len(monitors)):
            mon = monitors[i]
            print(f"{Fore.CYAN}[{i}] {Fore.WHITE}Monitor {i}")
            print(f"    Auflösung: {mon['width']}x{mon['height']}")
            print(f"    Position: X={mon['left']}, Y={mon['top']}")
            print()

        # User Input
        while True:
            try:
                choice = input(f"{Fore.YELLOW}Wähle Monitor (1-{len(monitors)-1}): {Fore.WHITE}")
                monitor_num = int(choice)

                if 1 <= monitor_num < len(monitors):
                    selected = monitors[monitor_num]
                    print(f"\n{Fore.GREEN}✓ Monitor {monitor_num} gewählt!")
                    print(f"  {selected['width']}x{selected['height']}\n")
                    return selected
                else:
                    print(f"{Fore.RED}Ungültige Auswahl! Wähle zwischen 1 und {len(monitors)-1}")
            except ValueError:
                print(f"{Fore.RED}Bitte eine Zahl eingeben!")
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Abgebrochen.")
                exit(0)

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
