"""
Enemy Detector - nutzt unser trainiertes YOLO Model!
====================================================
Wrapper um das CS2 Detection Model.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../cs2-aimbot-ml'))

from PIL import ImageGrab
import numpy as np
import torch
from ultralytics import YOLO

class EnemyDetector:
    def __init__(self, model_path="../cs2-aimbot-ml/models/cs2_target_detector_n/weights/best.pt"):
        """
        Enemy Detector using our trained YOLO model

        Args:
            model_path: Path to trained YOLO model
        """
        self.model_path = model_path
        self.model = None
        self.class_names = {
            0: "ct_body", 1: "ct_head", 2: "ct_legs",
            3: "t_body", 4: "t_head", 5: "t_legs"
        }

        # Load model
        self.load_model()

    def load_model(self):
        """Load YOLO model"""
        if not os.path.exists(self.model_path):
            print(f"❌ Model nicht gefunden: {self.model_path}")
            print(f"Trainiere erst ein Model mit dem CS2-Aimbot-ML Tool!")
            return False

        print(f"Loading model from: {self.model_path}")
        self.model = YOLO(self.model_path)

        # GPU wenn verfügbar
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Using device: {self.device}")

        return True

    def detect(self, image, conf_threshold=0.4, my_team='CT'):
        """
        Detect enemies in image

        Args:
            image: PIL Image or numpy array
            conf_threshold: Confidence threshold
            my_team: 'CT' or 'T' - only detect enemies!

        Returns:
            detections: List of (x, y, w, h, class_name, confidence, is_head)
        """
        if self.model is None:
            return []

        # Run detection
        results = self.model.predict(
            image,
            conf=conf_threshold,
            device=self.device,
            verbose=False
        )[0]

        detections = []

        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            conf = float(box.conf[0])
            class_id = int(box.cls[0])
            class_name = self.class_names[class_id]

            # Nur Gegner erkennen!
            if my_team == 'CT' and class_id >= 3:  # T sind Gegner
                enemy = True
            elif my_team == 'T' and class_id < 3:  # CT sind Gegner
                enemy = True
            else:
                enemy = False

            if not enemy:
                continue

            # Box Dimensionen
            x = int(x1)
            y = int(y1)
            w = int(x2 - x1)
            h = int(y2 - y1)

            # Ist es ein Kopf?
            is_head = 'head' in class_name

            # Center point
            center_x = x + w // 2
            center_y = y + h // 2

            detections.append({
                'bbox': (x, y, w, h),
                'center': (center_x, center_y),
                'class': class_name,
                'conf': conf,
                'is_head': is_head,
                'team': 'T' if class_id >= 3 else 'CT'
            })

        # Sortiere nach Confidence (beste zuerst)
        detections.sort(key=lambda d: d['conf'], reverse=True)

        return detections

    def get_closest_enemy(self, detections, screen_center=(960, 540)):
        """
        Get enemy closest to crosshair

        Args:
            detections: List from detect()
            screen_center: Crosshair position (x, y)

        Returns:
            Best target detection or None
        """
        if not detections:
            return None

        # Berechne Distanz zum Crosshair
        def distance_to_crosshair(det):
            cx, cy = det['center']
            dx = cx - screen_center[0]
            dy = cy - screen_center[1]
            return dx**2 + dy**2

        # Priorisiere Köpfe!
        heads = [d for d in detections if d['is_head']]

        if heads:
            # Nächster Kopf zum Crosshair
            return min(heads, key=distance_to_crosshair)
        else:
            # Nächster Body
            return min(detections, key=distance_to_crosshair)

    def get_threat_level(self, detections):
        """
        Calculate threat level (0-10)

        Returns:
            threat: 0 = safe, 10 = extreme danger
        """
        if not detections:
            return 0.0

        threat = 0.0

        # Anzahl Gegner
        threat += len(detections) * 2.0

        # Wie nah am Crosshair?
        for det in detections:
            cx, cy = det['center']
            dist = ((cx - 960)**2 + (cy - 540)**2) ** 0.5

            # Nah = gefährlich
            if dist < 100:
                threat += 3.0
            elif dist < 300:
                threat += 1.5
            elif dist < 500:
                threat += 0.5

        return min(threat, 10.0)


if __name__ == "__main__":
    # Test
    print("🎯 Testing Enemy Detector...")

    detector = EnemyDetector()

    if detector.model:
        print("\n✅ Model loaded successfully!")
        print("Ready to detect enemies!")

        # Test mit Screenshot
        print("\nTaking screenshot...")
        img = ImageGrab.grab()

        print("Detecting enemies...")
        detections = detector.detect(img, my_team='CT')

        print(f"\nFound {len(detections)} enemies:")
        for i, det in enumerate(detections):
            print(f"  {i+1}. {det['class']} - Conf: {det['conf']:.2f} - Pos: {det['center']}")

        if detections:
            target = detector.get_closest_enemy(detections)
            print(f"\n🎯 Best target: {target['class']} at {target['center']}")

            threat = detector.get_threat_level(detections)
            print(f"⚠️  Threat level: {threat:.1f}/10")
    else:
        print("\n❌ Model not found. Train a model first!")
