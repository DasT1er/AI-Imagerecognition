"""
CS2 Target Labeling Tool
========================
Einfaches Tool zum Markieren von Gegnern in Screenshots.

Verwendung:
1. Screenshots mit capture_screenshots.py sammeln
2. Dieses Script starten
3. Klicke und ziehe um Bounding Boxes um Gegner zu zeichnen
4. Drücke 's' zum Speichern und weiter zum nächsten Bild
5. Drücke 'd' um Bild zu überspringen (kein Gegner sichtbar)
6. Drücke 'q' zum Beenden

Labels werden im YOLO-Format gespeichert (data/labeled/).
"""

import cv2
import os
import numpy as np
from pathlib import Path
from colorama import Fore, init

init(autoreset=True)

class TargetLabeler:
    def __init__(self, input_dir="../data/raw", output_dir="../data/labeled"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.images_output = os.path.join(output_dir, "images")
        self.labels_output = os.path.join(output_dir, "labels")

        os.makedirs(self.images_output, exist_ok=True)
        os.makedirs(self.labels_output, exist_ok=True)

        # Lade alle Bilder
        self.image_files = sorted([f for f in os.listdir(input_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
        self.current_idx = 0

        # Bounding Box state
        self.drawing = False
        self.boxes = []
        self.current_box = None
        self.start_point = None

        print(f"{Fore.GREEN}{'='*60}")
        print(f"{Fore.CYAN}CS2 Target Labeling Tool")
        print(f"{Fore.GREEN}{'='*60}")
        print(f"{Fore.YELLOW}Steuerung:")
        print(f"  Maus - Ziehe Box um Gegner")
        print(f"  s    - Speichern & nächstes Bild")
        print(f"  d    - Überspringen (kein Gegner)")
        print(f"  u    - Letzte Box rückgängig")
        print(f"  r    - Alle Boxes löschen")
        print(f"  q    - Beenden")
        print(f"{Fore.GREEN}{'='*60}\n")
        print(f"{Fore.WHITE}Gefundene Bilder: {Fore.CYAN}{len(self.image_files)}")
        print(f"{Fore.WHITE}Los geht's!\n")

    def mouse_callback(self, event, x, y, flags, param):
        """Maus-Event Handler für Bounding Box Zeichnung"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)

        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drawing:
                self.current_box = (self.start_point, (x, y))

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            if self.start_point:
                # Speichere die Box
                x1, y1 = self.start_point
                x2, y2 = x, y

                # Stelle sicher dass x1 < x2 und y1 < y2
                x1, x2 = min(x1, x2), max(x1, x2)
                y1, y2 = min(y1, y2), max(y1, y2)

                # Nur speichern wenn Box groß genug ist
                if abs(x2 - x1) > 10 and abs(y2 - y1) > 10:
                    self.boxes.append((x1, y1, x2, y2))
                    print(f"{Fore.GREEN}  ✓ Box hinzugefügt: ({x1}, {y1}) -> ({x2}, {y2})")

                self.current_box = None
                self.start_point = None

    def convert_to_yolo_format(self, box, img_width, img_height):
        """Konvertiert Box zu YOLO Format (x_center, y_center, width, height) - normalisiert"""
        x1, y1, x2, y2 = box

        x_center = ((x1 + x2) / 2) / img_width
        y_center = ((y1 + y2) / 2) / img_height
        width = (x2 - x1) / img_width
        height = (y2 - y1) / img_height

        return x_center, y_center, width, height

    def save_labels(self, image_filename):
        """Speichert Labels im YOLO Format"""
        if not self.boxes:
            print(f"{Fore.YELLOW}  ⚠ Keine Boxes markiert, überspringe...")
            return

        # Lade Bild um Dimensionen zu bekommen
        img_path = os.path.join(self.input_dir, image_filename)
        img = cv2.imread(img_path)
        h, w = img.shape[:2]

        # Kopiere Bild
        output_img_path = os.path.join(self.images_output, image_filename)
        cv2.imwrite(output_img_path, img)

        # Speichere Labels
        label_filename = os.path.splitext(image_filename)[0] + '.txt'
        label_path = os.path.join(self.labels_output, label_filename)

        with open(label_path, 'w') as f:
            for box in self.boxes:
                x_center, y_center, width, height = self.convert_to_yolo_format(box, w, h)
                # Class 0 = enemy
                f.write(f"0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

        print(f"{Fore.GREEN}✓ Gespeichert: {len(self.boxes)} Targets in {image_filename}")

    def run(self):
        """Hauptloop für Labeling"""
        if not self.image_files:
            print(f"{Fore.RED}Keine Bilder gefunden in {self.input_dir}")
            print(f"{Fore.YELLOW}Tipp: Führe zuerst capture_screenshots.py aus!")
            return

        cv2.namedWindow('CS2 Target Labeling')
        cv2.setMouseCallback('CS2 Target Labeling', self.mouse_callback)

        while self.current_idx < len(self.image_files):
            image_file = self.image_files[self.current_idx]
            img_path = os.path.join(self.input_dir, image_file)

            # Lade Bild
            img = cv2.imread(img_path)
            if img is None:
                print(f"{Fore.RED}Fehler beim Laden von {image_file}")
                self.current_idx += 1
                continue

            display_img = img.copy()

            # Zeige Info
            progress = f"{self.current_idx + 1}/{len(self.image_files)}"
            cv2.putText(display_img, progress, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(display_img, f"Boxes: {len(self.boxes)}", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Zeichne gespeicherte Boxes
            for box in self.boxes:
                x1, y1, x2, y2 = box
                cv2.rectangle(display_img, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Zeichne aktuelle Box (während Ziehen)
            if self.current_box:
                pt1, pt2 = self.current_box
                cv2.rectangle(display_img, pt1, pt2, (0, 0, 255), 2)

            cv2.imshow('CS2 Target Labeling', display_img)

            key = cv2.waitKey(1) & 0xFF

            # Speichern und weiter
            if key == ord('s'):
                self.save_labels(image_file)
                self.boxes = []
                self.current_idx += 1

            # Überspringen
            elif key == ord('d'):
                print(f"{Fore.YELLOW}⊘ Übersprungen: {image_file}")
                self.boxes = []
                self.current_idx += 1

            # Letzte Box rückgängig
            elif key == ord('u'):
                if self.boxes:
                    removed = self.boxes.pop()
                    print(f"{Fore.YELLOW}  ↶ Letzte Box entfernt")

            # Alle Boxes löschen
            elif key == ord('r'):
                self.boxes = []
                print(f"{Fore.YELLOW}  ✗ Alle Boxes gelöscht")

            # Beenden
            elif key == ord('q'):
                print(f"\n{Fore.YELLOW}Labeling beendet.")
                break

        cv2.destroyAllWindows()
        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"{Fore.GREEN}Fertig! Gelabelte Bilder: {self.current_idx}")
        print(f"{Fore.CYAN}Bilder: {self.images_output}")
        print(f"{Fore.CYAN}Labels: {self.labels_output}")
        print(f"{Fore.GREEN}{'='*60}")

if __name__ == "__main__":
    try:
        labeler = TargetLabeler()
        labeler.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Programm beendet.")
