from typing import Dict
from helpers.common import fimg_from_dir
from helpers.ocr import ocr_license_plate
from helpers.yolo import yolo_inference
from helpers.sw import records_to_txt, smith_waterman

DATA_CONFIG: Dict[str, Dict[str, str]] = {
    "sw": {
        "name": "Smith-Waterman",
        "data_dir": "data/hsa/small",
        "data_type": "text",
        "preprocess": records_to_txt,
        "process": smith_waterman,
    },
    "ocr": {
        "name": "Optical Character Recognition",
        "data_dir": "data/license_plates",
        "data_type": "image",
        "preprocess": fimg_from_dir,
        "process": ocr_license_plate,
    }, 
    "yolo": {
        "name": "Object Detection",
        "data_dir": "data/coco128_images",
        "data_type": "image",
        "preprocess": fimg_from_dir,
        "process": yolo_inference,
    },
}
