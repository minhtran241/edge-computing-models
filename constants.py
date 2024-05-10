from typing import Dict
from ultralytics import YOLO

IMAGE_DIR: str = "data/license_plates"
# IMAGE_DIR: str = "data/coco128/images/train2017"

ALGORITHMS: Dict[str, Dict[str, str]] = {
    "ocr": {
        "name": "Optical Character Recognition",
        "data_dir": "data/license_plates",
        "data_type": "image",
    },
    "yolo": {
        "name": "Object Detection",
        "data_dir": "data/coco128/images/train2017",
        "data_type": "image",
    },
    "lda": {
        "name": "Latent Dirichlet Allocation",
        "data_dir": "data/text",
        "data_type": "text",
    },
}

YOLO_MODEL: YOLO = YOLO("yolov8m.pt")
