"""
CS2 Advanced Labeling Tool - Multi-Class
=========================================
Professionelles Labeling-Tool für Gegner UND Köpfe!

Features:
- Schönes UI mit Sidebar
- Zwei Klassen: Enemy (ganzer Körper) + Head (Kopf)
- Farbcodierung: Grün = Enemy, Rot = Head
- Einfaches Umschalten zwischen Modi
- Große Bildansicht + übersichtliche Controls

Verwendung:
1. Starte Tool
2. Wähle Modus: 'E' = Enemy / 'H' = Head
3. Ziehe Boxen
4. Speichere mit 'S'

Mit diesem Tool lernt die AI BEIDE:
- Wo der Gegner ist (ganze Box)
- Wo der Kopf ist (kleine Box)
→ Perfekte Headshots!
"""

import cv2
import os
import numpy as np
from pathlib import Path
from colorama import Fore, init

init(autoreset=True)

class AdvancedLabeler:
    def __init__(self, input_dir="../data/raw", output_dir="../data/labeled_advanced"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.images_output = os.path.join(output_dir, "images")
        self.labels_output = os.path.join(output_dir, "labels")

        os.makedirs(self.images_output, exist_ok=True)
        os.makedirs(self.labels_output, exist_ok=True)

        # Lade Bilder
        self.image_files = sorted([f for f in os.listdir(input_dir)
                                   if f.endswith(('.png', '.jpg', '.jpeg'))])
        self.current_idx = 0

        # Klassen
        self.CLASS_ENEMY = 0  # Ganzer Gegner
        self.CLASS_HEAD = 1   # Nur Kopf
        self.current_class = self.CLASS_ENEMY

        # Farben
        self.COLOR_ENEMY = (0, 255, 0)    # Grün
        self.COLOR_HEAD = (0, 0, 255)     # Rot
        self.COLOR_SIDEBAR = (40, 40, 40) # Dunkelgrau
        self.COLOR_ACTIVE = (0, 255, 255) # Gelb

        # State
        self.drawing = False
        self.boxes = []  # Format: [(x1, y1, x2, y2, class), ...]
        self.current_box = None
        self.start_point = None

        # UI Größen
        self.sidebar_width = 250
        self.window_name = 'CS2 Advanced Labeling'

        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.CYAN}CS2 Advanced Multi-Class Labeling Tool")
        print(f"{Fore.GREEN}{'='*70}\n")
        print(f"{Fore.YELLOW}Klassen:")
        print(f"  {Fore.GREEN}[E] Enemy{Fore.WHITE} - Ganzer Gegner (Grün)")
        print(f"  {Fore.RED}[H] Head{Fore.WHITE}  - Nur Kopf (Rot)\n")
        print(f"{Fore.YELLOW}Steuerung:")
        print(f"  E / H    - Wechsel zwischen Enemy/Head Modus")
        print(f"  Maus     - Ziehe Box")
        print(f"  S        - Speichern & nächstes Bild")
        print(f"  D        - Überspringen")
        print(f"  U        - Letzte Box löschen")
        print(f"  R        - Alle Boxes löschen")
        print(f"  Q        - Beenden")
        print(f"\n{Fore.CYAN}Workflow:")
        print(f"  1. Drücke 'E' → Ziehe Box um GANZEN Gegner (Grün)")
        print(f"  2. Drücke 'H' → Ziehe Box um NUR KOPF (Rot)")
        print(f"  3. Wiederhole für alle Gegner im Bild")
        print(f"  4. Drücke 'S' zum Speichern")
        print(f"\n{Fore.GREEN}{'='*70}\n")
        print(f"{Fore.WHITE}Gefundene Bilder: {Fore.CYAN}{len(self.image_files)}")
        print(f"{Fore.GREEN}Los geht's!\n")

    def get_class_color(self, class_id):
        """Gibt Farbe für Klasse zurück"""
        return self.COLOR_ENEMY if class_id == self.CLASS_ENEMY else self.COLOR_HEAD

    def get_class_name(self, class_id):
        """Gibt Klassen-Namen zurück"""
        return "Enemy" if class_id == self.CLASS_ENEMY else "Head"

    def draw_sidebar(self, height):
        """Erstellt Sidebar"""
        sidebar = np.zeros((height, self.sidebar_width, 3), dtype=np.uint8)
        sidebar[:] = self.COLOR_SIDEBAR

        y_offset = 30

        # Titel
        cv2.putText(sidebar, "LABELING MODE", (10, y_offset),
                   cv2.FONT_HERSHEY_BOLD, 0.6, (255, 255, 255), 2)
        y_offset += 40

        # Separator
        cv2.line(sidebar, (10, y_offset), (self.sidebar_width-10, y_offset),
                (100, 100, 100), 1)
        y_offset += 30

        # Enemy Button
        enemy_active = (self.current_class == self.CLASS_ENEMY)
        enemy_color = self.COLOR_ACTIVE if enemy_active else self.COLOR_ENEMY
        cv2.rectangle(sidebar, (10, y_offset), (self.sidebar_width-10, y_offset+50),
                     enemy_color, -1 if enemy_active else 2)
        cv2.putText(sidebar, "[E] ENEMY", (20, y_offset+32),
                   cv2.FONT_HERSHEY_BOLD, 0.7, (0, 0, 0) if enemy_active else (255, 255, 255), 2)
        y_offset += 70

        # Head Button
        head_active = (self.current_class == self.CLASS_HEAD)
        head_color = self.COLOR_ACTIVE if head_active else self.COLOR_HEAD
        cv2.rectangle(sidebar, (10, y_offset), (self.sidebar_width-10, y_offset+50),
                     head_color, -1 if head_active else 2)
        cv2.putText(sidebar, "[H] HEAD", (20, y_offset+32),
                   cv2.FONT_HERSHEY_BOLD, 0.7, (0, 0, 0) if head_active else (255, 255, 255), 2)
        y_offset += 80

        # Separator
        cv2.line(sidebar, (10, y_offset), (self.sidebar_width-10, y_offset),
                (100, 100, 100), 1)
        y_offset += 30

        # Statistiken
        enemy_count = sum(1 for box in self.boxes if box[4] == self.CLASS_ENEMY)
        head_count = sum(1 for box in self.boxes if box[4] == self.CLASS_HEAD)

        cv2.putText(sidebar, "STATISTICS", (10, y_offset),
                   cv2.FONT_HERSHEY_BOLD, 0.6, (255, 255, 255), 2)
        y_offset += 30

        cv2.putText(sidebar, f"Enemies: {enemy_count}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLOR_ENEMY, 1)
        y_offset += 25

        cv2.putText(sidebar, f"Heads: {head_count}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLOR_HEAD, 1)
        y_offset += 25

        cv2.putText(sidebar, f"Total: {len(self.boxes)}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y_offset += 40

        # Separator
        cv2.line(sidebar, (10, y_offset), (self.sidebar_width-10, y_offset),
                (100, 100, 100), 1)
        y_offset += 30

        # Hilfe
        cv2.putText(sidebar, "CONTROLS", (10, y_offset),
                   cv2.FONT_HERSHEY_BOLD, 0.6, (255, 255, 255), 2)
        y_offset += 30

        controls = [
            ("S", "Save"),
            ("D", "Skip"),
            ("U", "Undo"),
            ("R", "Reset"),
            ("Q", "Quit")
        ]

        for key, action in controls:
            cv2.putText(sidebar, f"{key} - {action}", (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
            y_offset += 20

        return sidebar

    def mouse_callback(self, event, x, y, flags, param):
        """Maus-Event Handler"""
        # Ignoriere Clicks in Sidebar
        if x >= param['img_width']:
            return

        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.current_box = (self.start_point, (x, y))

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            if self.start_point:
                x1, y1 = self.start_point
                x2, y2 = x, y

                x1, x2 = min(x1, x2), max(x1, x2)
                y1, y2 = min(y1, y2), max(y1, y2)

                width = x2 - x1
                height = y2 - y1

                # Validierung
                if width > 10 and height > 10:
                    # Warnung bei Head-Box die zu groß ist
                    if self.current_class == self.CLASS_HEAD and (width > 150 or height > 150):
                        print(f"{Fore.YELLOW}  ⚠️  Head-Box sehr groß ({width}x{height}px) - Sicher dass das nur der Kopf ist?")

                    # Warnung bei Enemy-Box die zu klein ist
                    if self.current_class == self.CLASS_ENEMY and (width < 30 or height < 50):
                        print(f"{Fore.YELLOW}  ⚠️  Enemy-Box sehr klein ({width}x{height}px) - Sicher dass das der ganze Gegner ist?")

                    self.boxes.append((x1, y1, x2, y2, self.current_class))
                    class_name = self.get_class_name(self.current_class)
                    color_name = "Grün" if self.current_class == self.CLASS_ENEMY else "Rot"
                    print(f"{Fore.GREEN}  ✓ {class_name} Box hinzugefügt ({width}x{height}px) - {color_name}")

                self.current_box = None
                self.start_point = None

    def convert_to_yolo_format(self, box, img_width, img_height):
        """Konvertiert Box zu YOLO Format"""
        x1, y1, x2, y2, class_id = box

        x_center = ((x1 + x2) / 2) / img_width
        y_center = ((y1 + y2) / 2) / img_height
        width = (x2 - x1) / img_width
        height = (y2 - y1) / img_height

        return class_id, x_center, y_center, width, height

    def save_labels(self, image_filename):
        """Speichert Labels im YOLO Format"""
        if not self.boxes:
            print(f"{Fore.YELLOW}  ⚠ Keine Boxen markiert, überspringe...")
            return

        img_path = os.path.join(self.input_dir, image_filename)
        img = cv2.imread(img_path)
        h, w = img.shape[:2]

        # Kopiere Bild
        output_img_path = os.path.join(self.images_output, image_filename)
        cv2.imwrite(output_img_path, img)

        # Speichere Labels
        label_filename = os.path.splitext(image_filename)[0] + '.txt'
        label_path = os.path.join(self.labels_output, label_filename)

        enemy_count = 0
        head_count = 0

        with open(label_path, 'w') as f:
            for box in self.boxes:
                class_id, x_center, y_center, width, height = self.convert_to_yolo_format(box, w, h)
                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

                if class_id == self.CLASS_ENEMY:
                    enemy_count += 1
                else:
                    head_count += 1

        print(f"{Fore.GREEN}✓ Gespeichert: {enemy_count} Enemies (Grün) + {head_count} Heads (Rot) in {image_filename}")

    def run(self):
        """Hauptloop"""
        if not self.image_files:
            print(f"{Fore.RED}Keine Bilder gefunden in {self.input_dir}")
            print(f"{Fore.YELLOW}Tipp: Führe zuerst capture_screenshots.py aus!")
            return

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)

        while self.current_idx < len(self.image_files):
            image_file = self.image_files[self.current_idx]
            img_path = os.path.join(self.input_dir, image_file)

            img = cv2.imread(img_path)
            if img is None:
                print(f"{Fore.RED}Fehler beim Laden von {image_file}")
                self.current_idx += 1
                continue

            h, w = img.shape[:2]

            # Erstelle Display mit Sidebar
            display_img = img.copy()

            # Zeichne gespeicherte Boxen
            for box in self.boxes:
                x1, y1, x2, y2, class_id = box
                color = self.get_class_color(class_id)
                thickness = 3 if class_id == self.CLASS_HEAD else 2

                cv2.rectangle(display_img, (x1, y1), (x2, y2), color, thickness)

                # Label
                label = self.get_class_name(class_id)
                label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)

                # Label Background
                cv2.rectangle(display_img,
                            (x1, y1 - label_size[1] - 10),
                            (x1 + label_size[0] + 5, y1),
                            color, -1)

                # Label Text
                cv2.putText(display_img, label, (x1 + 2, y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

                # Kreuz in der Mitte
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                cv2.drawMarker(display_img, (cx, cy), color, cv2.MARKER_CROSS, 15, 2)

            # Zeichne aktuelle Box
            if self.current_box:
                pt1, pt2 = self.current_box
                color = self.get_class_color(self.current_class)
                cv2.rectangle(display_img, pt1, pt2, color, 2)

            # Info Overlay
            info_y = 30
            progress = f"Image {self.current_idx + 1}/{len(self.image_files)}"
            cv2.putText(display_img, progress, (10, info_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            # Aktueller Modus
            mode_text = f"Mode: {self.get_class_name(self.current_class)}"
            mode_color = self.get_class_color(self.current_class)
            cv2.putText(display_img, mode_text, (10, info_y + 40),
                       cv2.FONT_HERSHEY_BOLD, 0.8, mode_color, 2)

            # Erstelle Sidebar
            sidebar = self.draw_sidebar(h)

            # Kombiniere Bild + Sidebar
            combined = np.hstack([display_img, sidebar])

            cv2.imshow(self.window_name, combined)

            # Setze Mouse Callback mit img_width als Parameter
            cv2.setMouseCallback(self.window_name, self.mouse_callback, {'img_width': w})

            key = cv2.waitKey(1) & 0xFF

            # Klassen-Wechsel
            if key == ord('e') or key == ord('E'):
                self.current_class = self.CLASS_ENEMY
                print(f"{Fore.GREEN}► Modus: ENEMY (Ganzer Gegner - Grün)")

            elif key == ord('h') or key == ord('H'):
                self.current_class = self.CLASS_HEAD
                print(f"{Fore.RED}► Modus: HEAD (Nur Kopf - Rot)")

            # Speichern
            elif key == ord('s') or key == ord('S'):
                self.save_labels(image_file)
                self.boxes = []
                self.current_idx += 1

            # Überspringen
            elif key == ord('d') or key == ord('D'):
                print(f"{Fore.YELLOW}⊘ Übersprungen: {image_file}")
                self.boxes = []
                self.current_idx += 1

            # Undo
            elif key == ord('u') or key == ord('U'):
                if self.boxes:
                    removed = self.boxes.pop()
                    class_name = self.get_class_name(removed[4])
                    print(f"{Fore.YELLOW}  ↶ {class_name} Box entfernt")

            # Reset
            elif key == ord('r') or key == ord('R'):
                self.boxes = []
                print(f"{Fore.YELLOW}  ✗ Alle Boxes gelöscht")

            # Beenden
            elif key == ord('q') or key == ord('Q'):
                print(f"\n{Fore.YELLOW}Labeling beendet.")
                break

        cv2.destroyAllWindows()

        # Finale Statistik
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"{Fore.GREEN}Fertig! Gelabelte Bilder: {self.current_idx}")
        print(f"{Fore.CYAN}Bilder: {self.images_output}")
        print(f"{Fore.CYAN}Labels: {self.labels_output}")
        print(f"\n{Fore.YELLOW}Nächste Schritte:")
        print(f"{Fore.WHITE}1. Führe prepare_dataset.py aus")
        print(f"{Fore.WHITE}2. Trainiere Multi-Class Model (2_training/train_model.py)")
        print(f"{Fore.WHITE}3. AI kennt jetzt BEIDE: Gegner + Köpfe!")
        print(f"{Fore.GREEN}{'='*70}")

if __name__ == "__main__":
    try:
        labeler = AdvancedLabeler()
        labeler.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Programm beendet.")
