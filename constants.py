import os
from typing import List
from ultralytics import YOLO

VALID_ROLES: List[str] = ["iot", "edge", "cloud"]
DEFAULT_ITERATIONS: int = 100
YOLO_MODEL: YOLO = YOLO(model=os.getenv("YOLOV8_MODEL_PATH") or "yolov8m.pt")
