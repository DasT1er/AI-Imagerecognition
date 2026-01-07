"""
CS2 6-Class Labeling - Volle Team-Separation
==============================================
Professionelles Labeling-Tool für 6 Klassen:
CT Team:
- CT Body (Körper/Gegner)
- CT Head (Kopf)
- CT Legs (Beine)

T Team:
- T Body (Körper/Gegner)
- T Head (Kopf)
- T Legs (Beine)

Features:
- Team-Auswahl mit TAB
- 6 separate Klassen
- Schönes UI mit Sidebar
"""

import cv2
import os
import numpy as np
from colorama import Fore, init

init(autoreset=True)

class SixClassLabeler:
    def __init__(self, input_dir="../data/raw", output_dir="../data/labeled_6class"):
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

        # 6 Klassen!
        self.CLASS_CT_BODY = 0
        self.CLASS_CT_HEAD = 1
        self.CLASS_CT_LEGS = 2
        self.CLASS_T_BODY = 3
        self.CLASS_T_HEAD = 4
        self.CLASS_T_LEGS = 5

        # Team-Modus (CT oder T)
        self.current_team = 'CT'  # Start mit CT
        self.current_part = 'BODY'  # BODY, HEAD, LEGS

        # Farben
        self.COLOR_CT = (255, 150, 0)     # Blau
        self.COLOR_T = (0, 165, 255)      # Orange
        self.COLOR_HEAD = (0, 255, 0)     # Grün
        self.COLOR_LEGS = (255, 0, 255)   # Magenta
        self.COLOR_BODY = (255, 255, 0)   # Cyan
        self.COLOR_SIDEBAR = (40, 40, 40)
        self.COLOR_ACTIVE = (0, 255, 255)

        # State
        self.drawing = False
        self.boxes = []  # Format: [(x1, y1, x2, y2, class), ...]
        self.current_box = None
        self.start_point = None

        # UI
        self.sidebar_width = 350
        self.window_name = 'CS2 6-Class Labeling'

        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.CYAN}CS2 6-Class Labeling Tool - Vollständige Team-Trennung")
        print(f"{Fore.GREEN}{'='*70}\n")
        print(f"{Fore.YELLOW}6 Klassen:")
        print(f"  {Fore.BLUE}CT Team:")
        print(f"    [1] CT Body  - Körper/Gegner")
        print(f"    [2] CT Head  - Kopf")
        print(f"    [3] CT Legs  - Beine")
        print(f"  {Fore.YELLOW}T Team:")
        print(f"    [4] T Body   - Körper/Gegner")
        print(f"    [5] T Head   - Kopf")
        print(f"    [6] T Legs   - Beine")
        print(f"\n{Fore.YELLOW}Steuerung:")
        print(f"  TAB      - Team wechseln (CT ↔ T)")
        print(f"  B        - Body Mode")
        print(f"  H        - Head Mode")
        print(f"  L        - Legs Mode")
        print(f"  1-6      - Direkte Klassenwahl")
        print(f"  Maus     - Box ziehen")
        print(f"  S        - Speichern")
        print(f"  D        - Überspringen")
        print(f"  U        - Letzte Box löschen")
        print(f"  Q        - Beenden")
        print(f"\n{Fore.CYAN}Workflow pro Bild:")
        print(f"  1. TAB drücken um Team zu wählen (CT oder T)")
        print(f"  2. B/H/L drücken für Body/Head/Legs")
        print(f"  3. Box um Spieler-Teil ziehen")
        print(f"  4. Für jeden Spieler wiederholen")
        print(f"  5. S drücken zum Speichern")
        print(f"\n{Fore.GREEN}{'='*70}\n")
        print(f"{Fore.WHITE}Gefundene Bilder: {Fore.CYAN}{len(self.image_files)}\n")

    def get_current_class(self):
        """Gibt aktuelle Klasse basierend auf Team und Part zurück"""
        if self.current_team == 'CT':
            if self.current_part == 'BODY':
                return self.CLASS_CT_BODY
            elif self.current_part == 'HEAD':
                return self.CLASS_CT_HEAD
            elif self.current_part == 'LEGS':
                return self.CLASS_CT_LEGS
        else:  # T
            if self.current_part == 'BODY':
                return self.CLASS_T_BODY
            elif self.current_part == 'HEAD':
                return self.CLASS_T_HEAD
            elif self.current_part == 'LEGS':
                return self.CLASS_T_LEGS
        return 0

    def get_class_color(self, class_id):
        """Gibt Farbe für Klasse zurück"""
        if class_id in [self.CLASS_CT_BODY, self.CLASS_CT_HEAD, self.CLASS_CT_LEGS]:
            # CT Team - Blau für Body, Grün für Head, Magenta für Legs
            if class_id == self.CLASS_CT_BODY:
                return self.COLOR_BODY
            elif class_id == self.CLASS_CT_HEAD:
                return self.COLOR_HEAD
            else:
                return self.COLOR_LEGS
        else:
            # T Team - Gleiche Farblogik aber leicht anders
            if class_id == self.CLASS_T_BODY:
                return self.COLOR_BODY
            elif class_id == self.CLASS_T_HEAD:
                return self.COLOR_HEAD
            else:
                return self.COLOR_LEGS

    def get_class_name(self, class_id):
        """Gibt Klassen-Namen zurück"""
        names = {
            self.CLASS_CT_BODY: "CT Body",
            self.CLASS_CT_HEAD: "CT Head",
            self.CLASS_CT_LEGS: "CT Legs",
            self.CLASS_T_BODY: "T Body",
            self.CLASS_T_HEAD: "T Head",
            self.CLASS_T_LEGS: "T Legs"
        }
        return names.get(class_id, "Unknown")

    def draw_sidebar(self, height):
        """Erstellt Sidebar"""
        sidebar = np.zeros((height, self.sidebar_width, 3), dtype=np.uint8)
        sidebar[:] = self.COLOR_SIDEBAR

        y_offset = 30

        # Titel
        cv2.putText(sidebar, "LABELING MODE", (10, y_offset),
                   cv2.FONT_HERSHEY_BOLD, 0.7, (255, 255, 255), 2)
        y_offset += 40

        cv2.line(sidebar, (10, y_offset), (self.sidebar_width-10, y_offset),
                (100, 100, 100), 1)
        y_offset += 30

        # Team-Auswahl
        team_color = self.COLOR_CT if self.current_team == 'CT' else self.COLOR_T
        cv2.putText(sidebar, f"TEAM: {self.current_team}", (10, y_offset),
                   cv2.FONT_HERSHEY_BOLD, 0.8, team_color, 2)
        cv2.putText(sidebar, "(TAB to switch)", (10, y_offset + 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        y_offset += 55

        cv2.line(sidebar, (10, y_offset), (self.sidebar_width-10, y_offset),
                (100, 100, 100), 1)
        y_offset += 30

        # Part-Auswahl
        parts = ['BODY', 'HEAD', 'LEGS']
        colors = [self.COLOR_BODY, self.COLOR_HEAD, self.COLOR_LEGS]
        keys = ['B', 'H', 'L']

        for i, (part, color, key) in enumerate(zip(parts, colors, keys)):
            is_active = (self.current_part == part)
            btn_color = self.COLOR_ACTIVE if is_active else color

            cv2.rectangle(sidebar, (10, y_offset), (self.sidebar_width-10, y_offset+45),
                         btn_color, -1 if is_active else 2)

            text = f"[{key}] {part}"
            cv2.putText(sidebar, text, (20, y_offset+28),
                       cv2.FONT_HERSHEY_BOLD, 0.6, (0, 0, 0) if is_active else (255, 255, 255), 2)
            y_offset += 55

        y_offset += 10
        cv2.line(sidebar, (10, y_offset), (self.sidebar_width-10, y_offset),
                (100, 100, 100), 1)
        y_offset += 30

        # Aktueller Modus
        current_class = self.get_current_class()
        current_name = self.get_class_name(current_class)
        cv2.putText(sidebar, "CURRENT:", (10, y_offset),
                   cv2.FONT_HERSHEY_BOLD, 0.6, (255, 255, 255), 2)
        y_offset += 25
        cv2.putText(sidebar, current_name, (10, y_offset),
                   cv2.FONT_HERSHEY_BOLD, 0.7, self.get_class_color(current_class), 2)
        y_offset += 35

        cv2.line(sidebar, (10, y_offset), (self.sidebar_width-10, y_offset),
                (100, 100, 100), 1)
        y_offset += 30

        # Statistiken
        ct_body = sum(1 for box in self.boxes if box[4] == self.CLASS_CT_BODY)
        ct_head = sum(1 for box in self.boxes if box[4] == self.CLASS_CT_HEAD)
        ct_legs = sum(1 for box in self.boxes if box[4] == self.CLASS_CT_LEGS)
        t_body = sum(1 for box in self.boxes if box[4] == self.CLASS_T_BODY)
        t_head = sum(1 for box in self.boxes if box[4] == self.CLASS_T_HEAD)
        t_legs = sum(1 for box in self.boxes if box[4] == self.CLASS_T_LEGS)

        cv2.putText(sidebar, "STATISTICS", (10, y_offset),
                   cv2.FONT_HERSHEY_BOLD, 0.6, (255, 255, 255), 2)
        y_offset += 30

        cv2.putText(sidebar, "CT Team:", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLOR_CT, 1)
        y_offset += 20
        cv2.putText(sidebar, f"  Body: {ct_body}  Head: {ct_head}  Legs: {ct_legs}", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
        y_offset += 25

        cv2.putText(sidebar, "T Team:", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLOR_T, 1)
        y_offset += 20
        cv2.putText(sidebar, f"  Body: {t_body}  Head: {t_head}  Legs: {t_legs}", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
        y_offset += 35

        cv2.line(sidebar, (10, y_offset), (self.sidebar_width-10, y_offset),
                (100, 100, 100), 1)
        y_offset += 30

        # Controls
        cv2.putText(sidebar, "CONTROLS", (10, y_offset),
                   cv2.FONT_HERSHEY_BOLD, 0.6, (255, 255, 255), 2)
        y_offset += 30

        controls = [
            ("TAB", "Switch Team"),
            ("B/H/L", "Body/Head/Legs"),
            ("1-6", "Direct Class"),
            ("S", "Save"),
            ("D", "Skip"),
            ("U", "Undo"),
            ("Q", "Quit")
        ]

        for key, action in controls:
            cv2.putText(sidebar, f"{key} - {action}", (15, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
            y_offset += 18

        return sidebar

    def mouse_callback(self, event, x, y, flags, param):
        """Maus-Event Handler"""
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

                if width > 10 and height > 10:
                    current_class = self.get_current_class()

                    # Warnungen
                    if self.current_part == 'HEAD' and (width > 150 or height > 150):
                        print(f"{Fore.YELLOW}  ⚠️  Head-Box sehr groß ({width}x{height}px)")

                    if self.current_part == 'LEGS' and height > 200:
                        print(f"{Fore.YELLOW}  ⚠️  Legs-Box sehr hoch ({width}x{height}px)")

                    if self.current_part == 'BODY' and (width < 30 or height < 50):
                        print(f"{Fore.YELLOW}  ⚠️  Body-Box sehr klein ({width}x{height}px)")

                    self.boxes.append((x1, y1, x2, y2, current_class))
                    class_name = self.get_class_name(current_class)
                    print(f"{Fore.GREEN}  ✓ {class_name} Box hinzugefügt ({width}x{height}px)")

                self.current_box = None
                self.start_point = None

    def convert_to_yolo_format(self, box, img_width, img_height):
        """Konvertiert zu YOLO Format"""
        x1, y1, x2, y2, class_id = box

        x_center = ((x1 + x2) / 2) / img_width
        y_center = ((y1 + y2) / 2) / img_height
        width = (x2 - x1) / img_width
        height = (y2 - y1) / img_height

        return class_id, x_center, y_center, width, height

    def save_labels(self, image_filename):
        """Speichert Labels"""
        if not self.boxes:
            print(f"{Fore.YELLOW}  ⚠ Keine Boxen markiert")
            return

        img_path = os.path.join(self.input_dir, image_filename)
        img = cv2.imread(img_path)
        h, w = img.shape[:2]

        output_img_path = os.path.join(self.images_output, image_filename)
        cv2.imwrite(output_img_path, img)

        label_filename = os.path.splitext(image_filename)[0] + '.txt'
        label_path = os.path.join(self.labels_output, label_filename)

        counts = {i: 0 for i in range(6)}

        with open(label_path, 'w') as f:
            for box in self.boxes:
                class_id, x_center, y_center, width, height = self.convert_to_yolo_format(box, w, h)
                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
                counts[class_id] += 1

        print(f"{Fore.GREEN}✓ Gespeichert:")
        print(f"  CT: Body:{counts[0]} Head:{counts[1]} Legs:{counts[2]}")
        print(f"  T:  Body:{counts[3]} Head:{counts[4]} Legs:{counts[5]}")

    def run(self):
        """Hauptloop"""
        if not self.image_files:
            print(f"{Fore.RED}Keine Bilder gefunden")
            return

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)

        while self.current_idx < len(self.image_files):
            image_file = self.image_files[self.current_idx]
            img_path = os.path.join(self.input_dir, image_file)

            img = cv2.imread(img_path)
            if img is None:
                self.current_idx += 1
                continue

            h, w = img.shape[:2]
            display_img = img.copy()

            # Zeichne Boxen
            for box in self.boxes:
                x1, y1, x2, y2, class_id = box
                color = self.get_class_color(class_id)

                # Team-basierte Border
                if class_id in [self.CLASS_CT_BODY, self.CLASS_CT_HEAD, self.CLASS_CT_LEGS]:
                    border_color = self.COLOR_CT
                else:
                    border_color = self.COLOR_T

                # Doppelter Border für Team-Identifikation
                cv2.rectangle(display_img, (x1-2, y1-2), (x2+2, y2+2), border_color, 2)
                cv2.rectangle(display_img, (x1, y1), (x2, y2), color, 2)

                label = self.get_class_name(class_id)
                # Label mit Team-Farbe
                cv2.putText(display_img, label, (x1 + 2, y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, border_color, 2)

                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                cv2.drawMarker(display_img, (cx, cy), color, cv2.MARKER_CROSS, 15, 2)

            # Aktuelle Box
            if self.current_box:
                pt1, pt2 = self.current_box
                current_class = self.get_current_class()
                color = self.get_class_color(current_class)
                cv2.rectangle(display_img, pt1, pt2, color, 2)

            # Info
            progress = f"{self.current_idx + 1}/{len(self.image_files)}"
            cv2.putText(display_img, progress, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            current_class = self.get_current_class()
            mode_text = f"Mode: {self.get_class_name(current_class)}"
            mode_color = self.get_class_color(current_class)
            cv2.putText(display_img, mode_text, (10, 70),
                       cv2.FONT_HERSHEY_BOLD, 0.8, mode_color, 2)

            # Sidebar
            sidebar = self.draw_sidebar(h)
            combined = np.hstack([display_img, sidebar])

            cv2.imshow(self.window_name, combined)
            cv2.setMouseCallback(self.window_name, self.mouse_callback, {'img_width': w})

            key = cv2.waitKey(1) & 0xFF

            # Team-Wechsel
            if key == 9:  # TAB
                self.current_team = 'T' if self.current_team == 'CT' else 'CT'
                team_color = "Blau" if self.current_team == 'CT' else "Orange"
                print(f"{Fore.CYAN}► Team gewechselt: {self.current_team} ({team_color})")

            # Part-Wechsel
            elif key == ord('b') or key == ord('B'):
                self.current_part = 'BODY'
                print(f"{Fore.CYAN}► Modus: {self.current_team} BODY")
            elif key == ord('h') or key == ord('H'):
                self.current_part = 'HEAD'
                print(f"{Fore.GREEN}► Modus: {self.current_team} HEAD")
            elif key == ord('l') or key == ord('L'):
                self.current_part = 'LEGS'
                print(f"{Fore.MAGENTA}► Modus: {self.current_team} LEGS")

            # Direkte Klassenwahl
            elif key == ord('1'):
                self.current_team = 'CT'
                self.current_part = 'BODY'
                print(f"{Fore.BLUE}► Modus: CT BODY")
            elif key == ord('2'):
                self.current_team = 'CT'
                self.current_part = 'HEAD'
                print(f"{Fore.BLUE}► Modus: CT HEAD")
            elif key == ord('3'):
                self.current_team = 'CT'
                self.current_part = 'LEGS'
                print(f"{Fore.BLUE}► Modus: CT LEGS")
            elif key == ord('4'):
                self.current_team = 'T'
                self.current_part = 'BODY'
                print(f"{Fore.YELLOW}► Modus: T BODY")
            elif key == ord('5'):
                self.current_team = 'T'
                self.current_part = 'HEAD'
                print(f"{Fore.YELLOW}► Modus: T HEAD")
            elif key == ord('6'):
                self.current_team = 'T'
                self.current_part = 'LEGS'
                print(f"{Fore.YELLOW}► Modus: T LEGS")

            elif key == ord('s') or key == ord('S'):
                self.save_labels(image_file)
                self.boxes = []
                self.current_idx += 1

            elif key == ord('d') or key == ord('D'):
                print(f"{Fore.YELLOW}⊘ Übersprungen")
                self.boxes = []
                self.current_idx += 1

            elif key == ord('u') or key == ord('U'):
                if self.boxes:
                    removed = self.boxes.pop()
                    print(f"{Fore.YELLOW}  ↶ {self.get_class_name(removed[4])} Box entfernt")

            elif key == ord('q') or key == ord('Q'):
                break

        cv2.destroyAllWindows()
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"{Fore.GREEN}Fertig! Gelabelte Bilder: {self.current_idx}")
        print(f"{Fore.GREEN}{'='*70}")

if __name__ == "__main__":
    try:
        labeler = SixClassLabeler()
        labeler.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Beendet.")
