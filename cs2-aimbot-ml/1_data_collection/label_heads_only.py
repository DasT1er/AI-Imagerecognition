"""
CS2 Head-Only Labeling Tool
============================
Spezielles Tool zum Markieren von NUR KÖPFEN für präzise Headshots.

Verwendung:
1. Screenshots mit capture_screenshots.py sammeln
2. Dieses Script starten
3. Ziehe kleine Boxen um NUR DEN KOPF (nicht ganzer Körper!)
4. Trainiere separates Head-Detection Model

Vorteile:
- Viel präzisere Headshot-Erkennung
- Funktioniert auch bei Hocken/Springen
- Bessere Auto-Aim Performance
"""

import cv2
import os
import numpy as np
from pathlib import Path
from colorama import Fore, init

init(autoreset=True)

class HeadLabeler:
    def __init__(self, input_dir="../data/raw", output_dir="../data/heads_labeled"):
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
        print(f"{Fore.CYAN}CS2 Head-Only Labeling Tool")
        print(f"{Fore.GREEN}{'='*60}")
        print(f"{Fore.YELLOW}Steuerung:")
        print(f"  Maus - Ziehe Box um NUR DEN KOPF!")
        print(f"  s    - Speichern & nächstes Bild")
        print(f"  d    - Überspringen")
        print(f"  u    - Letzte Box rückgängig")
        print(f"  r    - Alle Boxes löschen")
        print(f"  q    - Beenden")
        print(f"{Fore.GREEN}{'='*60}\n")
        print(f"{Fore.RED}⚠️  WICHTIG: Markiere NUR DEN KOPF, NICHT den ganzen Körper!")
        print(f"{Fore.YELLOW}Tipp: Box sollte klein sein - nur Kopf/Helm!\n")
        print(f"{Fore.WHITE}Gefundene Bilder: {Fore.CYAN}{len(self.image_files)}")
        print(f"{Fore.WHITE}Los geht's!\n")

    def mouse_callback(self, event, x, y, flags, param):
        """Maus-Event Handler"""
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

                # Check ob Box nicht zu groß ist (Kopf sollte klein sein!)
                width = x2 - x1
                height = y2 - y1

                if abs(x2 - x1) > 10 and abs(y2 - y1) > 10:
                    # Warnung wenn Box sehr groß ist
                    if width > 150 or height > 150:
                        print(f"{Fore.YELLOW}  ⚠️  Box ist sehr groß ({width}x{height}px) - Ist das wirklich nur der Kopf?")

                    self.boxes.append((x1, y1, x2, y2))
                    print(f"{Fore.GREEN}  ✓ Kopf-Box hinzugefügt: {width}x{height}px")

                self.current_box = None
                self.start_point = None

    def convert_to_yolo_format(self, box, img_width, img_height):
        """Konvertiert Box zu YOLO Format"""
        x1, y1, x2, y2 = box

        x_center = ((x1 + x2) / 2) / img_width
        y_center = ((y1 + y2) / 2) / img_height
        width = (x2 - x1) / img_width
        height = (y2 - y1) / img_height

        return x_center, y_center, width, height

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

        with open(label_path, 'w') as f:
            for box in self.boxes:
                x_center, y_center, width, height = self.convert_to_yolo_format(box, w, h)
                # Class 0 = head
                f.write(f"0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

        print(f"{Fore.GREEN}✓ Gespeichert: {len(self.boxes)} Köpfe in {image_filename}")

    def run(self):
        """Hauptloop"""
        if not self.image_files:
            print(f"{Fore.RED}Keine Bilder gefunden in {self.input_dir}")
            return

        cv2.namedWindow('CS2 Head Labeling')
        cv2.setMouseCallback('CS2 Head Labeling', self.mouse_callback)

        while self.current_idx < len(self.image_files):
            image_file = self.image_files[self.current_idx]
            img_path = os.path.join(self.input_dir, image_file)

            img = cv2.imread(img_path)
            if img is None:
                print(f"{Fore.RED}Fehler beim Laden von {image_file}")
                self.current_idx += 1
                continue

            display_img = img.copy()

            # Info
            progress = f"{self.current_idx + 1}/{len(self.image_files)}"
            cv2.putText(display_img, progress, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(display_img, f"Heads: {len(self.boxes)}", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(display_img, "HEAD ONLY!", (10, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # Zeichne gespeicherte Boxes (Rot für Köpfe)
            for box in self.boxes:
                x1, y1, x2, y2 = box
                cv2.rectangle(display_img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                # Kreuz in der Mitte
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                cv2.drawMarker(display_img, (cx, cy), (0, 0, 255), cv2.MARKER_CROSS, 15, 2)

            # Zeichne aktuelle Box
            if self.current_box:
                pt1, pt2 = self.current_box
                cv2.rectangle(display_img, pt1, pt2, (0, 255, 255), 2)

            cv2.imshow('CS2 Head Labeling', display_img)

            key = cv2.waitKey(1) & 0xFF

            if key == ord('s'):
                self.save_labels(image_file)
                self.boxes = []
                self.current_idx += 1

            elif key == ord('d'):
                print(f"{Fore.YELLOW}⊘ Übersprungen: {image_file}")
                self.boxes = []
                self.current_idx += 1

            elif key == ord('u'):
                if self.boxes:
                    removed = self.boxes.pop()
                    print(f"{Fore.YELLOW}  ↶ Letzte Box entfernt")

            elif key == ord('r'):
                self.boxes = []
                print(f"{Fore.YELLOW}  ✗ Alle Boxes gelöscht")

            elif key == ord('q'):
                print(f"\n{Fore.YELLOW}Labeling beendet.")
                break

        cv2.destroyAllWindows()
        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"{Fore.GREEN}Fertig! Gelabelte Bilder: {self.current_idx}")
        print(f"{Fore.CYAN}Bilder: {self.images_output}")
        print(f"{Fore.CYAN}Labels: {self.labels_output}")
        print(f"\n{Fore.YELLOW}Nächster Schritt:")
        print(f"{Fore.WHITE}1. Führe prepare_dataset_heads.py aus")
        print(f"{Fore.WHITE}2. Trainiere Head-Detection Model")
        print(f"{Fore.GREEN}{'='*60}")

if __name__ == "__main__":
    try:
        labeler = HeadLabeler()
        labeler.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Programm beendet.")
