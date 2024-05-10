import os
from ultralytics import YOLO

ITERATIONS: int = 100
YOLO_MODEL: YOLO = YOLO(model=os.getenv("YOLOV8_MODEL_PATH") or "yolov8m.pt")
