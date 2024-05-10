from typing import Dict
from helpers.common import image_to_bytes, read_txt
from helpers.ocr import ocr_license_plate
from helpers.yolo import yolo_inference
from helpers.sw import records_to_txt, smith_waterman

DATA_CONFIG: Dict[str, Dict[str, str]] = {
    "ocr": {
        "name": "Optical Character Recognition",
        "data_file": "data/license_plate.jpg",
        "data_type": "image",
        "preprocess": image_to_bytes,
        "process": ocr_license_plate,
    },
    "yolo": {
        "name": "Object Detection",
        "data_file": "data/objects.jpg",
        "data_type": "image",
        "preprocess": image_to_bytes,
        "process": yolo_inference,
    },
    "sw": {
        "name": "Smith-Waterman",
        "data_file": "data/hsa.txt",
        "data_type": "text",
        "preprocess": records_to_txt,
        "process": smith_waterman,
    },
}
