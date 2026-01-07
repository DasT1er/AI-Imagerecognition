"""
Semi-Automatic Labeling Tool
=============================
Nutzt ein bestehendes Model um neue Bilder VORZULABELN.
Du musst nur noch korrigieren statt von Grund auf zu labeln!

Workflow:
1. Model macht erste Predictions
2. Du korrigierst/ergänzt die Boxen
3. Speichern → 5x schneller als manuell!
"""

import cv2
import os
import numpy as np
from ultralytics import YOLO
from colorama import Fore, init

init(autoreset=True)

class SemiAutoLabeler:
    def __init__(self, model_path, input_dir="../data/raw", output_dir="../data/labeled_6class"):
        print(f"{Fore.GREEN}{'='*70}")
        print(f"{Fore.CYAN}Semi-Automatic Labeling Tool")
        print(f"{Fore.GREEN}{'='*70}\n")

        # Model laden
        if os.path.exists(model_path):
            print(f"{Fore.CYAN}Lade Model: {Fore.WHITE}{model_path}")
            self.model = YOLO(model_path)
            print(f"{Fore.GREEN}✓ Model geladen!\n")
        else:
            print(f"{Fore.YELLOW}⚠ Kein Model gefunden - starte ohne Pre-Labeling")
            self.model = None

        self.input_dir = input_dir
        self.output_dir = output_dir
        self.images_output = os.path.join(output_dir, "images")
        self.labels_output = os.path.join(output_dir, "labels")

        os.makedirs(self.images_output, exist_ok=True)
        os.makedirs(self.labels_output, exist_ok=True)

        # Sammle Bilder die noch nicht gelabelt sind
        existing_labels = set([os.path.splitext(f)[0] for f in os.listdir(self.labels_output)])
        all_images = [f for f in os.listdir(input_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]

        self.image_files = []
        for img in all_images:
            img_name = os.path.splitext(img)[0]
            if img_name not in existing_labels:
                self.image_files.append(img)

        self.current_idx = 0

        # Klassen
        self.CLASS_CT_BODY = 0
        self.CLASS_CT_HEAD = 1
        self.CLASS_CT_LEGS = 2
        self.CLASS_T_BODY = 3
        self.CLASS_T_HEAD = 4
        self.CLASS_T_LEGS = 5

        # Team und Part State
        self.current_team = 'CT'
        self.current_part = 'BODY'

        # Farben
        self.COLOR_CT = (255, 150, 0)
        self.COLOR_T = (0, 165, 255)
        self.COLOR_BODY = (255, 255, 0)
        self.COLOR_HEAD = (0, 255, 0)
        self.COLOR_LEGS = (255, 0, 255)
        self.COLOR_SIDEBAR = (40, 40, 40)
        self.COLOR_ACTIVE = (0, 255, 255)

        # State
        self.drawing = False
        self.boxes = []
        self.current_box = None
        self.start_point = None
        self.sidebar_width = 350

        print(f"{Fore.YELLOW}Gefundene Bilder: {Fore.WHITE}{len(all_images)}")
        print(f"{Fore.GREEN}Bereits gelabelt: {Fore.WHITE}{len(existing_labels)}")
        print(f"{Fore.CYAN}Noch zu labeln: {Fore.WHITE}{len(self.image_files)}\n")

        if self.model:
            print(f"{Fore.GREEN}✓ Semi-Auto Mode aktiv!")
            print(f"{Fore.CYAN}Model macht Pre-Predictions, du korrigierst nur!\n")
        else:
            print(f"{Fore.YELLOW}Manueller Mode - labele wie gewohnt\n")

        print(f"{Fore.YELLOW}Steuerung:")
        print(f"  TAB      - Team wechseln (CT/T)")
        print(f"  B/H/L    - Body/Head/Legs")
        print(f"  DELETE   - Ausgewählte Box löschen")
        print(f"  A        - Auto-Predict akzeptieren")
        print(f"  S        - Speichern")
        print(f"  D        - Überspringen")
        print(f"{Fore.GREEN}{'='*70}\n")

    def get_current_class(self):
        if self.current_team == 'CT':
            if self.current_part == 'BODY':
                return self.CLASS_CT_BODY
            elif self.current_part == 'HEAD':
                return self.CLASS_CT_HEAD
            else:
                return self.CLASS_CT_LEGS
        else:
            if self.current_part == 'BODY':
                return self.CLASS_T_BODY
            elif self.current_part == 'HEAD':
                return self.CLASS_T_HEAD
            else:
                return self.CLASS_T_LEGS

    def auto_predict(self, img):
        """Macht automatische Predictions"""
        if self.model is None:
            return []

        results = self.model.predict(img, conf=0.3, verbose=False)[0]

        boxes = []
        if results.boxes is not None:
            for box in results.boxes:
                class_id = int(box.cls[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                boxes.append((x1, y1, x2, y2, class_id))

        return boxes

    def get_class_color(self, class_id):
        if class_id in [self.CLASS_CT_BODY, self.CLASS_CT_HEAD, self.CLASS_CT_LEGS]:
            if class_id == self.CLASS_CT_BODY:
                return self.COLOR_BODY
            elif class_id == self.CLASS_CT_HEAD:
                return self.COLOR_HEAD
            else:
                return self.COLOR_LEGS
        else:
            if class_id == self.CLASS_T_BODY:
                return self.COLOR_BODY
            elif class_id == self.CLASS_T_HEAD:
                return self.COLOR_HEAD
            else:
                return self.COLOR_LEGS

    def get_class_name(self, class_id):
        names = {
            0: "CT Body", 1: "CT Head", 2: "CT Legs",
            3: "T Body", 4: "T Head", 5: "T Legs"
        }
        return names.get(class_id, "Unknown")

    def mouse_callback(self, event, x, y, flags, param):
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

                if (x2 - x1) > 10 and (y2 - y1) > 10:
                    current_class = self.get_current_class()
                    self.boxes.append((x1, y1, x2, y2, current_class))
                    print(f"{Fore.GREEN}  ✓ {self.get_class_name(current_class)} hinzugefügt")

                self.current_box = None
                self.start_point = None

    def convert_to_yolo(self, box, w, h):
        x1, y1, x2, y2, class_id = box
        x_center = ((x1 + x2) / 2) / w
        y_center = ((y1 + y2) / 2) / h
        width = (x2 - x1) / w
        height = (y2 - y1) / h
        return class_id, x_center, y_center, width, height

    def save_labels(self, image_filename):
        if not self.boxes:
            print(f"{Fore.YELLOW}  ⚠ Keine Boxen")
            return

        img_path = os.path.join(self.input_dir, image_filename)
        img = cv2.imread(img_path)
        h, w = img.shape[:2]

        output_img = os.path.join(self.images_output, image_filename)
        cv2.imwrite(output_img, img)

        label_file = os.path.join(self.labels_output, os.path.splitext(image_filename)[0] + '.txt')

        with open(label_file, 'w') as f:
            for box in self.boxes:
                class_id, xc, yc, bw, bh = self.convert_to_yolo(box, w, h)
                f.write(f"{class_id} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}\n")

        print(f"{Fore.GREEN}✓ Gespeichert: {len(self.boxes)} boxes")

    def run(self):
        if not self.image_files:
            print(f"{Fore.GREEN}Alle Bilder bereits gelabelt!")
            return

        cv2.namedWindow('Semi-Auto Labeling', cv2.WINDOW_NORMAL)

        while self.current_idx < len(self.image_files):
            img_file = self.image_files[self.current_idx]
            img_path = os.path.join(self.input_dir, img_file)
            img = cv2.imread(img_path)

            if img is None:
                self.current_idx += 1
                continue

            print(f"\n{Fore.CYAN}[{self.current_idx+1}/{len(self.image_files)}] {img_file}")

            # Auto-Predict beim ersten Mal
            if not self.boxes and self.model:
                print(f"{Fore.YELLOW}  → Auto-Predicting...")
                self.boxes = self.auto_predict(img)
                if self.boxes:
                    print(f"{Fore.GREEN}  ✓ {len(self.boxes)} Predictions gefunden!")
                    print(f"{Fore.CYAN}  Korrigiere/ergänze und drücke S zum Speichern")
                    print(f"{Fore.CYAN}  Oder A zum Akzeptieren")

            h, w = img.shape[:2]

            while True:
                display = img.copy()

                # Zeichne Boxen
                for box in self.boxes:
                    x1, y1, x2, y2, cid = box
                    color = self.get_class_color(cid)

                    # Team border
                    border = self.COLOR_CT if cid < 3 else self.COLOR_T
                    cv2.rectangle(display, (x1-2, y1-2), (x2+2, y2+2), border, 2)
                    cv2.rectangle(display, (x1, y1), (x2, y2), color, 2)

                    label = self.get_class_name(cid)
                    cv2.putText(display, label, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, border, 2)

                # Current box
                if self.current_box:
                    pt1, pt2 = self.current_box
                    color = self.get_class_color(self.get_current_class())
                    cv2.rectangle(display, pt1, pt2, color, 2)

                # Info
                info = f"{self.current_idx+1}/{len(self.image_files)} | Team: {self.current_team} | Part: {self.current_part}"
                cv2.putText(display, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                cv2.imshow('Semi-Auto Labeling', display)
                cv2.setMouseCallback('Semi-Auto Labeling', self.mouse_callback, {'img_width': w})

                key = cv2.waitKey(1) & 0xFF

                if key == 9:  # TAB
                    self.current_team = 'T' if self.current_team == 'CT' else 'CT'
                    print(f"{Fore.CYAN}► Team: {self.current_team}")

                elif key == ord('b') or key == ord('B'):
                    self.current_part = 'BODY'
                    print(f"{Fore.CYAN}► Part: BODY")
                elif key == ord('h') or key == ord('H'):
                    self.current_part = 'HEAD'
                    print(f"{Fore.GREEN}► Part: HEAD")
                elif key == ord('l') or key == ord('L'):
                    self.current_part = 'LEGS'
                    print(f"{Fore.MAGENTA}► Part: LEGS")

                elif key == ord('a') or key == ord('A'):
                    # Akzeptiere Auto-Predictions
                    if self.boxes:
                        self.save_labels(img_file)
                        self.boxes = []
                        self.current_idx += 1
                        break

                elif key == ord('s') or key == ord('S'):
                    self.save_labels(img_file)
                    self.boxes = []
                    self.current_idx += 1
                    break

                elif key == ord('d') or key == ord('D'):
                    print(f"{Fore.YELLOW}⊘ Übersprungen")
                    self.boxes = []
                    self.current_idx += 1
                    break

                elif key == 127 or key == 8:  # DELETE/BACKSPACE
                    if self.boxes:
                        removed = self.boxes.pop()
                        print(f"{Fore.YELLOW}  ↶ {self.get_class_name(removed[4])} entfernt")

                elif key == ord('q') or key == ord('Q'):
                    cv2.destroyAllWindows()
                    return

        cv2.destroyAllWindows()
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"{Fore.GREEN}Fertig!")
        print(f"{Fore.GREEN}{'='*70}")

if __name__ == "__main__":
    import sys

    model_path = "../models/cs2_target_detector_n/weights/best.pt"

    if len(sys.argv) > 1:
        model_path = sys.argv[1]

    labeler = SemiAutoLabeler(model_path)
    labeler.run()
