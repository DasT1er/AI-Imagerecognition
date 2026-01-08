"""
CS2 Auto-Screenshot Tool - DXCam (OBS-Style)
=============================================
Nutzt die GLEICHE Methode wie OBS - Windows Graphics Capture API!

DXCam:
+ Nutzt DirectX Desktop Duplication API
+ GLEICHE Technologie wie OBS
+ Beste Farbgenauigkeit
+ Schnellste Performance
+ Keine Überbelichtung
+ Funktioniert perfekt mit Fullscreen-Spielen

DIES IST DIE BESTE METHODE FÜR CS2!
"""

import time
import os
from datetime import datetime
from colorama import Fore, init
import numpy as np
from PIL import Image

init(autoreset=True)

class AutoScreenshotDXCam:
    def __init__(self, output_dir="../data/raw", interval_seconds=2.0, target_fps=None):
        """
        Auto-Screenshot Tool mit DXCam (OBS-Methode!)

        Args:
            output_dir: Wo Screenshots gespeichert werden
            interval_seconds: Sekunden zwischen Screenshots
            target_fps: Optional - FPS für Video-Capture
        """
        self.output_dir = output_dir
        self.interval = interval_seconds
        os.makedirs(output_dir, exist_ok=True)
        self.screenshot_count = 0

        # DXCam importieren
        try:
            import dxcam
            self.dxcam = dxcam
            self.camera = dxcam.create(output_color="BGR")

            print(f"\n{Fore.GREEN}{'='*60}")
            print(f"{Fore.CYAN}CS2 Auto-Screenshot Tool - DXCam (OBS-Methode!)")
            print(f"{Fore.GREEN}{'='*60}")
            print(f"{Fore.GREEN}✓ DXCam erfolgreich geladen!")
            print(f"{Fore.YELLOW}Einstellungen:")
            print(f"  Methode: {Fore.CYAN}Windows Graphics Capture API (wie OBS!)")
            print(f"  Interval: {Fore.CYAN}{interval_seconds} Sekunden")
            print(f"  Ausgabe: {Fore.CYAN}{output_dir}")
            print(f"\n{Fore.GREEN}Vorteile dieser Methode:")
            print(f"  • GLEICHE Technologie wie OBS")
            print(f"  • Beste Farbgenauigkeit")
            print(f"  • Keine Ueberbelichtung")
            print(f"  • Funktioniert mit Fullscreen")
            print(f"  • Ultra-schnell (GPU-basiert)")
            print(f"\n{Fore.WHITE}Macht automatisch alle {interval_seconds}s einen Screenshot!")
            print(f"{Fore.YELLOW}Druecke STRG+C zum Beenden\n")
            print(f"{Fore.GREEN}{'='*60}\n")

        except ImportError:
            print(f"\n{Fore.RED}{'='*60}")
            print(f"{Fore.RED}FEHLER: DXCam nicht installiert!")
            print(f"{Fore.RED}{'='*60}\n")
            print(f"{Fore.YELLOW}Installiere DXCam mit:")
            print(f"{Fore.WHITE}  pip install dxcam\n")
            print(f"{Fore.CYAN}DXCam nutzt die gleiche Methode wie OBS!")
            print(f"{Fore.GREEN}Danach funktionieren Screenshots perfekt!\n")
            raise

    def capture_screenshot(self):
        """Macht einen Screenshot mit DXCam (OBS-Methode)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"cs2_screenshot_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)

        # Screenshot mit DXCam (wie OBS!)
        frame = self.camera.grab()

        if frame is not None:
            # BGR -> RGB konvertieren
            frame_rgb = frame[:, :, ::-1]
            img = Image.fromarray(frame_rgb)
            img.save(filepath)

            self.screenshot_count += 1
            print(f"{Fore.GREEN}✓ Screenshot #{self.screenshot_count}: {Fore.CYAN}{filename}")
        else:
            print(f"{Fore.YELLOW}⚠ Frame capture fehlgeschlagen (CS2 minimiert?)")

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
        finally:
            # Cleanup
            if hasattr(self, 'camera'):
                self.camera.release()
                print(f"{Fore.GREEN}DXCam freigegeben.\n")

if __name__ == "__main__":
    # EINSTELLUNGEN HIER ANPASSEN:
    try:
        capturer = AutoScreenshotDXCam(
            output_dir="../data/raw",
            interval_seconds=2.0    # Alle 2 Sekunden ein Screenshot
        )
        capturer.run()
    except ImportError:
        print(f"\n{Fore.RED}Kann nicht starten ohne DXCam!")
        print(f"{Fore.YELLOW}Installiere es mit: {Fore.WHITE}pip install dxcam\n")
