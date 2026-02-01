"""
YOLO-based object detector for CS2 player detection.
Wraps ultralytics YOLO for fast inference.
"""
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional
import time


@dataclass
class Detection:
    """Single detected object."""
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    class_id: int
    class_name: str = ""

    @property
    def center(self) -> tuple:
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)

    @property
    def width(self) -> float:
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        return self.y2 - self.y1

    @property
    def area(self) -> float:
        return self.width * self.height

    def get_aim_point(self, bone: str = "head",
                      head_r: float = 0.15, neck_r: float = 0.25,
                      chest_r: float = 0.35, body_r: float = 0.50) -> tuple:
        """Get aim point based on bone selection."""
        cx = (self.x1 + self.x2) / 2
        ratios = {
            "head": head_r,
            "neck": neck_r,
            "chest": chest_r,
            "body": body_r,
        }
        ratio = ratios.get(bone, head_r)
        cy = self.y1 + self.height * ratio
        return (cx, cy)


class YOLODetector:
    """YOLO detector wrapper with performance tracking."""

    def __init__(self, model_path: str, device: str = "cuda",
                 conf: float = 0.45, imgsz: int = 640,
                 half: bool = True, verbose: bool = False):
        from ultralytics import YOLO

        self.model = YOLO(model_path)
        self.device = device
        self.conf = conf
        self.imgsz = imgsz
        self.half = half and device == "cuda"
        self.verbose = verbose
        self.inference_time = 0.0

        # Warmup
        dummy = np.zeros((imgsz, imgsz, 3), dtype=np.uint8)
        self.model.predict(
            dummy, device=device, imgsz=imgsz,
            half=self.half, verbose=False, conf=conf
        )

    def detect(self, frame: np.ndarray,
               target_classes: Optional[List[int]] = None) -> List[Detection]:
        """Run detection on a frame. Returns list of Detection objects."""
        t0 = time.perf_counter()

        results = self.model.predict(
            frame,
            device=self.device,
            imgsz=self.imgsz,
            half=self.half,
            verbose=False,
            conf=self.conf,
        )

        self.inference_time = (time.perf_counter() - t0) * 1000  # ms

        detections = []
        if results and len(results) > 0:
            result = results[0]
            if result.boxes is not None:
                boxes = result.boxes
                for i in range(len(boxes)):
                    cls_id = int(boxes.cls[i].item())
                    if target_classes is not None and cls_id not in target_classes:
                        continue

                    x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy()
                    conf = float(boxes.conf[i].item())
                    name = result.names.get(cls_id, str(cls_id))

                    detections.append(Detection(
                        x1=float(x1), y1=float(y1),
                        x2=float(x2), y2=float(y2),
                        confidence=conf,
                        class_id=cls_id,
                        class_name=name,
                    ))

        return detections

    def set_confidence(self, conf: float):
        self.conf = conf
