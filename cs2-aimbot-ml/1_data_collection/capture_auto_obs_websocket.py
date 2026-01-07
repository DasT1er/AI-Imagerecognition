"""
CS2 Auto-Screenshot Tool - OBS WebSocket (Direkt über OBS!)
============================================================
Steuert OBS direkt und macht Screenshots über OBS selbst!

Voraussetzungen:
1. OBS muss laufen
2. OBS WebSocket Plugin aktiviert (in OBS 28+ eingebaut)
3. Python Package: pip install obsws-python

Vorteile:
+ DIREKT über OBS - perfekte Qualität
+ Nutzt deine OBS-Einstellungen
+ Keine zusätzliche CPU-Last
+ Screenshots exakt wie in OBS
"""

import time
import os
import shutil
from datetime import datetime
from colorama import Fore, init

init(autoreset=True)

class AutoScreenshotOBS:
    def __init__(self,
                 output_dir="../data/raw",
                 interval_seconds=2.0,
                 obs_host="localhost",
                 obs_port=4455,
                 obs_password=""):
        """
        Auto-Screenshot Tool via OBS WebSocket

        Args:
            output_dir: Wo Screenshots gespeichert werden
            interval_seconds: Sekunden zwischen Screenshots
            obs_host: OBS WebSocket Host (Standard: localhost)
            obs_port: OBS WebSocket Port (Standard: 4455)
            obs_password: OBS WebSocket Passwort (falls gesetzt)
        """
        self.output_dir = output_dir
        self.interval = interval_seconds
        os.makedirs(output_dir, exist_ok=True)
        self.screenshot_count = 0

        # OBS WebSocket importieren
        try:
            from obswebsocket import obsws, requests
            self.obsws = obsws
            self.requests = requests

            # Verbindung zu OBS
            print(f"\n{Fore.YELLOW}Verbinde zu OBS WebSocket...")
            self.ws = obsws(obs_host, obs_port, obs_password)
            self.ws.connect()

            # OBS Version prüfen
            version_info = self.ws.call(requests.GetVersion())

            print(f"\n{Fore.GREEN}{'='*60}")
            print(f"{Fore.CYAN}CS2 Auto-Screenshot Tool - OBS WebSocket")
            print(f"{Fore.GREEN}{'='*60}")
            print(f"{Fore.GREEN}✓ Verbunden mit OBS!")
            print(f"{Fore.CYAN}OBS Version: {version_info.getObsVersion()}")
            print(f"{Fore.YELLOW}Einstellungen:")
            print(f"  Methode: {Fore.CYAN}OBS WebSocket (DIREKT über OBS!)")
            print(f"  Interval: {Fore.CYAN}{interval_seconds} Sekunden")
            print(f"  Ausgabe: {Fore.CYAN}{output_dir}")
            print(f"\n{Fore.GREEN}Vorteile:")
            print(f"  • DIREKT über OBS")
            print(f"  • Perfekte Qualitaet")
            print(f"  • Nutzt deine OBS-Einstellungen")
            print(f"  • Keine zusaetzliche CPU-Last")
            print(f"\n{Fore.WHITE}Macht automatisch alle {interval_seconds}s einen Screenshot!")
            print(f"{Fore.YELLOW}Druecke STRG+C zum Beenden\n")
            print(f"{Fore.GREEN}{'='*60}\n")

        except ImportError:
            print(f"\n{Fore.RED}{'='*60}")
            print(f"{Fore.RED}FEHLER: obsws-python nicht installiert!")
            print(f"{Fore.RED}{'='*60}\n")
            print(f"{Fore.YELLOW}Installiere obsws-python mit:")
            print(f"{Fore.WHITE}  pip install obsws-python\n")
            print(f"{Fore.CYAN}Dann aktiviere WebSocket in OBS:")
            print(f"{Fore.WHITE}  OBS → Tools → WebSocket Server Settings")
            print(f"{Fore.WHITE}  Aktiviere 'Enable WebSocket server'\n")
            raise

        except Exception as e:
            print(f"\n{Fore.RED}{'='*60}")
            print(f"{Fore.RED}FEHLER: Kann nicht zu OBS verbinden!")
            print(f"{Fore.RED}{'='*60}\n")
            print(f"{Fore.YELLOW}Stelle sicher dass:")
            print(f"{Fore.WHITE}  1. OBS läuft")
            print(f"{Fore.WHITE}  2. WebSocket aktiviert ist:")
            print(f"{Fore.WHITE}     OBS → Tools → WebSocket Server Settings")
            print(f"{Fore.WHITE}     → Enable WebSocket server")
            print(f"{Fore.WHITE}  3. Port {obs_port} korrekt ist")
            print(f"{Fore.WHITE}  4. Passwort korrekt ist (falls gesetzt)\n")
            print(f"{Fore.RED}Fehler: {e}\n")
            raise

    def capture_screenshot(self):
        """Macht einen Screenshot über OBS"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"cs2_screenshot_{timestamp}.png"

        # OBS Screenshot-Pfad (temporär)
        temp_path = os.path.join(os.path.expanduser("~"), "Pictures", "obs_screenshot.png")
        final_path = os.path.join(self.output_dir, filename)

        try:
            # Screenshot via OBS machen
            self.ws.call(self.requests.SaveSourceScreenshot(
                sourceName="",  # Leer = ganzer Screen
                imageFormat="png",
                imageFilePath=temp_path,
                imageWidth=1920,  # Optional: Auflösung anpassen
                imageHeight=1080
            ))

            # Warte kurz bis Datei geschrieben ist
            time.sleep(0.1)

            # Verschiebe zu output_dir
            if os.path.exists(temp_path):
                shutil.move(temp_path, final_path)
                self.screenshot_count += 1
                print(f"{Fore.GREEN}✓ Screenshot #{self.screenshot_count}: {Fore.CYAN}{filename}")
            else:
                print(f"{Fore.YELLOW}⚠ Screenshot nicht gefunden")

        except Exception as e:
            print(f"{Fore.RED}✗ Screenshot fehlgeschlagen: {e}")

    def run(self):
        """Hauptloop"""
        print(f"{Fore.GREEN}Auto-Screenshot über OBS gestartet!")
        print(f"{Fore.CYAN}Spiele jetzt CS2 und OBS macht automatisch Screenshots...\n")

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
            if hasattr(self, 'ws'):
                self.ws.disconnect()
                print(f"{Fore.GREEN}OBS WebSocket getrennt.\n")

if __name__ == "__main__":
    # EINSTELLUNGEN HIER ANPASSEN:
    try:
        capturer = AutoScreenshotOBS(
            output_dir="../data/raw",
            interval_seconds=2.0,
            obs_host="localhost",
            obs_port=4455,
            obs_password=""  # Dein OBS WebSocket Passwort (falls gesetzt)
        )
        capturer.run()
    except (ImportError, Exception) as e:
        print(f"{Fore.RED}Kann nicht starten: {e}")
