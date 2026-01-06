"""
CS2 Advanced Multi-Class Labeling - Mit Team-Detection
=======================================================
Professionelles Labeling-Tool für 4 Klassen:
- Enemy CT (Counter-Terrorist - Blau)
- Enemy T (Terrorist - Orange)
- Head
- Legs

Features:
- Team-Unterscheidung
- 4 Klassen mit Farbcodierung
- Schönes UI mit Sidebar
"""

import cv2
import os
import numpy as np
from colorama import Fore, init

init(autoreset=True)

class TeamAwareLabeler:
    def __init__(self, input_dir="../data/raw", output_dir="../data/labeled_team_aware"):
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

        # Klassen (4 statt 2!)
        self.CLASS_ENEMY_CT = 0   # Counter-Terrorist (Blau)
        self.CLASS_ENEMY_T = 1    # Terrorist (Orange)
        self.CLASS_HEAD = 2       # Kopf (jedes Team)
        self.CLASS_LEGS = 3       # Beine (jedes Team)
        self.current_class = self.CLASS_ENEMY_CT

        # Farben
        self.COLOR_CT = (255, 100, 0)     # Blau
        self.COLOR_T = (0, 165, 255)      # Orange
        self.COLOR_HEAD = (0, 0, 255)     # Rot
        self.COLOR_LEGS = (255, 0, 255)   # Magenta
        self.COLOR_SIDEBAR = (40, 40, 40)
        self.COLOR_ACTIVE = (0, 255, 255)

        # State
        self.drawing = False
        self.boxes = []  # Format: [(x1, y1, x2, y2, class), ...]
        self.current_box = None
        self.start_point = None

        # UI
        self.sidebar_width = 300
        self.window_name = 'CS2 Team-Aware Labeling'

        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.CYAN}CS2 Team-Aware Multi-Class Labeling Tool")
        print(f"{Fore.GREEN}{'='*70}\n")
        print(f"{Fore.YELLOW}4 Klassen:")
        print(f"  {Fore.BLUE}[1] Enemy CT{Fore.WHITE} - Counter-Terrorist (Blau)")
        print(f"  {Fore.YELLOW}[2] Enemy T{Fore.WHITE}  - Terrorist (Orange)")
        print(f"  {Fore.RED}[3] Head{Fore.WHITE}     - Kopf (beide Teams)")
        print(f"  {Fore.MAGENTA}[4] Legs{Fore.WHITE}     - Beine (beide Teams)")
        print(f"\n{Fore.YELLOW}Steuerung:")
        print(f"  1/2/3/4  - Klassenwechsel")
        print(f"  Maus     - Box ziehen")
        print(f"  S        - Speichern")
        print(f"  D        - Überspringen")
        print(f"  U        - Letzte Box löschen")
        print(f"  Q        - Beenden")
        print(f"\n{Fore.CYAN}Workflow pro Bild:")
        print(f"  1. Erkenne Team: Blau (CT) oder Orange (T)")
        print(f"  2. Drücke 1 (CT) oder 2 (T)")
        print(f"  3. Ziehe Box um ganzen Gegner")
        print(f"  4. Drücke 3 → Box um Kopf")
        print(f"  5. Drücke 4 → Box um Beine")
        print(f"  6. Wiederhole für alle Gegner")
        print(f"  7. Drücke S zum Speichern")
        print(f"\n{Fore.GREEN}{'='*70}\n")
        print(f"{Fore.WHITE}Gefundene Bilder: {Fore.CYAN}{len(self.image_files)}\n")

    def get_class_color(self, class_id):
        """Gibt Farbe für Klasse zurück"""
        colors = {
            self.CLASS_ENEMY_CT: self.COLOR_CT,
            self.CLASS_ENEMY_T: self.COLOR_T,
            self.CLASS_HEAD: self.COLOR_HEAD,
            self.CLASS_LEGS: self.COLOR_LEGS
        }
        return colors.get(class_id, (255, 255, 255))

    def get_class_name(self, class_id):
        """Gibt Klassen-Namen zurück"""
        names = {
            self.CLASS_ENEMY_CT: "Enemy CT",
            self.CLASS_ENEMY_T: "Enemy T",
            self.CLASS_HEAD: "Head",
            self.CLASS_LEGS: "Legs"
        }
        return names.get(class_id, "Unknown")

    def draw_sidebar(self, height):
        """Erstellt Sidebar"""
        sidebar = np.zeros((height, self.sidebar_width, 3), dtype=np.uint8)
        sidebar[:] = self.COLOR_SIDEBAR

        y_offset = 30

        # Titel
        cv2.putText(sidebar, "LABELING MODE", (10, y_offset),
                   cv2.FONT_HERSHEY_BOLD, 0.6, (255, 255, 255), 2)
        y_offset += 40

        cv2.line(sidebar, (10, y_offset), (self.sidebar_width-10, y_offset),
                (100, 100, 100), 1)
        y_offset += 30

        # Enemy CT Button
        ct_active = (self.current_class == self.CLASS_ENEMY_CT)
        ct_color = self.COLOR_ACTIVE if ct_active else self.COLOR_CT
        cv2.rectangle(sidebar, (10, y_offset), (self.sidebar_width-10, y_offset+45),
                     ct_color, -1 if ct_active else 2)
        cv2.putText(sidebar, "[1] ENEMY CT", (20, y_offset+28),
                   cv2.FONT_HERSHEY_BOLD, 0.6, (0, 0, 0) if ct_active else (255, 255, 255), 2)
        y_offset += 60

        # Enemy T Button
        t_active = (self.current_class == self.CLASS_ENEMY_T)
        t_color = self.COLOR_ACTIVE if t_active else self.COLOR_T
        cv2.rectangle(sidebar, (10, y_offset), (self.sidebar_width-10, y_offset+45),
                     t_color, -1 if t_active else 2)
        cv2.putText(sidebar, "[2] ENEMY T", (20, y_offset+28),
                   cv2.FONT_HERSHEY_BOLD, 0.6, (0, 0, 0) if t_active else (255, 255, 255), 2)
        y_offset += 60

        # Head Button
        head_active = (self.current_class == self.CLASS_HEAD)
        head_color = self.COLOR_ACTIVE if head_active else self.COLOR_HEAD
        cv2.rectangle(sidebar, (10, y_offset), (self.sidebar_width-10, y_offset+45),
                     head_color, -1 if head_active else 2)
        cv2.putText(sidebar, "[3] HEAD", (20, y_offset+28),
                   cv2.FONT_HERSHEY_BOLD, 0.6, (0, 0, 0) if head_active else (255, 255, 255), 2)
        y_offset += 60

        # Legs Button
        legs_active = (self.current_class == self.CLASS_LEGS)
        legs_color = self.COLOR_ACTIVE if legs_active else self.COLOR_LEGS
        cv2.rectangle(sidebar, (10, y_offset), (self.sidebar_width-10, y_offset+45),
                     legs_color, -1 if legs_active else 2)
        cv2.putText(sidebar, "[4] LEGS", (20, y_offset+28),
                   cv2.FONT_HERSHEY_BOLD, 0.6, (0, 0, 0) if legs_active else (255, 255, 255), 2)
        y_offset += 70

        cv2.line(sidebar, (10, y_offset), (self.sidebar_width-10, y_offset),
                (100, 100, 100), 1)
        y_offset += 30

        # Statistiken
        ct_count = sum(1 for box in self.boxes if box[4] == self.CLASS_ENEMY_CT)
        t_count = sum(1 for box in self.boxes if box[4] == self.CLASS_ENEMY_T)
        head_count = sum(1 for box in self.boxes if box[4] == self.CLASS_HEAD)
        legs_count = sum(1 for box in self.boxes if box[4] == self.CLASS_LEGS)

        cv2.putText(sidebar, "STATISTICS", (10, y_offset),
                   cv2.FONT_HERSHEY_BOLD, 0.6, (255, 255, 255), 2)
        y_offset += 30

        cv2.putText(sidebar, f"Enemy CT: {ct_count}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLOR_CT, 1)
        y_offset += 25

        cv2.putText(sidebar, f"Enemy T: {t_count}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLOR_T, 1)
        y_offset += 25

        cv2.putText(sidebar, f"Heads: {head_count}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLOR_HEAD, 1)
        y_offset += 25

        cv2.putText(sidebar, f"Legs: {legs_count}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLOR_LEGS, 1)
        y_offset += 30

        cv2.line(sidebar, (10, y_offset), (self.sidebar_width-10, y_offset),
                (100, 100, 100), 1)
        y_offset += 30

        # Team-Hinweis
        cv2.putText(sidebar, "TEAM COLORS", (10, y_offset),
                   cv2.FONT_HERSHEY_BOLD, 0.6, (255, 255, 255), 2)
        y_offset += 30

        # CT Symbol (Blau)
        cv2.rectangle(sidebar, (20, y_offset-5), (40, y_offset+15),
                     self.COLOR_CT, -1)
        cv2.putText(sidebar, "= CT (Blue)", (50, y_offset+10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
        y_offset += 25

        # T Symbol (Orange)
        cv2.rectangle(sidebar, (20, y_offset-5), (40, y_offset+15),
                     self.COLOR_T, -1)
        cv2.putText(sidebar, "= T (Orange)", (50, y_offset+10),
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
            ("S", "Save"),
            ("D", "Skip"),
            ("U", "Undo"),
            ("Q", "Quit")
        ]

        for key, action in controls:
            cv2.putText(sidebar, f"{key} - {action}", (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
            y_offset += 20

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
                    # Warnungen
                    if self.current_class == self.CLASS_HEAD and (width > 150 or height > 150):
                        print(f"{Fore.YELLOW}  ⚠️  Head-Box sehr groß ({width}x{height}px)")

                    if self.current_class == self.CLASS_LEGS and height > 200:
                        print(f"{Fore.YELLOW}  ⚠️  Legs-Box sehr hoch ({width}x{height}px)")

                    if self.current_class in [self.CLASS_ENEMY_CT, self.CLASS_ENEMY_T] and (width < 30 or height < 50):
                        print(f"{Fore.YELLOW}  ⚠️  Enemy-Box sehr klein ({width}x{height}px)")

                    self.boxes.append((x1, y1, x2, y2, self.current_class))
                    class_name = self.get_class_name(self.current_class)
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

        counts = {0: 0, 1: 0, 2: 0, 3: 0}

        with open(label_path, 'w') as f:
            for box in self.boxes:
                class_id, x_center, y_center, width, height = self.convert_to_yolo_format(box, w, h)
                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
                counts[class_id] += 1

        print(f"{Fore.GREEN}✓ Gespeichert: CT:{counts[0]} T:{counts[1]} Heads:{counts[2]} Legs:{counts[3]}")

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
                thickness = 3 if class_id in [self.CLASS_HEAD, self.CLASS_LEGS] else 2

                cv2.rectangle(display_img, (x1, y1), (x2, y2), color, thickness)

                label = self.get_class_name(class_id)
                cv2.putText(display_img, label, (x1 + 2, y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                cv2.drawMarker(display_img, (cx, cy), color, cv2.MARKER_CROSS, 15, 2)

            # Aktuelle Box
            if self.current_box:
                pt1, pt2 = self.current_box
                color = self.get_class_color(self.current_class)
                cv2.rectangle(display_img, pt1, pt2, color, 2)

            # Info
            progress = f"{self.current_idx + 1}/{len(self.image_files)}"
            cv2.putText(display_img, progress, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            mode_text = f"Mode: {self.get_class_name(self.current_class)}"
            mode_color = self.get_class_color(self.current_class)
            cv2.putText(display_img, mode_text, (10, 70),
                       cv2.FONT_HERSHEY_BOLD, 0.8, mode_color, 2)

            # Sidebar
            sidebar = self.draw_sidebar(h)
            combined = np.hstack([display_img, sidebar])

            cv2.imshow(self.window_name, combined)
            cv2.setMouseCallback(self.window_name, self.mouse_callback, {'img_width': w})

            key = cv2.waitKey(1) & 0xFF

            # Klassen-Wechsel
            if key == ord('1'):
                self.current_class = self.CLASS_ENEMY_CT
                print(f"{Fore.BLUE}► Modus: ENEMY CT (Blau)")
            elif key == ord('2'):
                self.current_class = self.CLASS_ENEMY_T
                print(f"{Fore.YELLOW}► Modus: ENEMY T (Orange)")
            elif key == ord('3'):
                self.current_class = self.CLASS_HEAD
                print(f"{Fore.RED}► Modus: HEAD")
            elif key == ord('4'):
                self.current_class = self.CLASS_LEGS
                print(f"{Fore.MAGENTA}► Modus: LEGS")

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
                    self.boxes.pop()
                    print(f"{Fore.YELLOW}  ↶ Box entfernt")

            elif key == ord('q') or key == ord('Q'):
                break

        cv2.destroyAllWindows()
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"{Fore.GREEN}Fertig! Gelabelte Bilder: {self.current_idx}")
        print(f"{Fore.GREEN}{'='*70}")

if __name__ == "__main__":
    try:
        labeler = TeamAwareLabeler()
        labeler.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Beendet.")
