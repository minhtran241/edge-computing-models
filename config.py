from typing import Dict
from helpers.common import fimg_from_dir
from helpers.ocr import ocr_license_plate
from helpers.yolo import yolo_inference
from helpers.sw import collect_sw_data, smith_waterman
from helpers.sa import collect_sa_data, sentiment_analysis

DATA_CONFIG: Dict[str, Dict[str, str]] = {
    "sw": {
        "name": "Smith-Waterman",
        "data_dir": "data/seq_align",
        "data_type": "text",
        "available_sizes": ["small", "medium", "large"],
        "preprocess": collect_sw_data,
        "process": smith_waterman,
    },
    "sa": {
        "name": "Sentiment Analysis",
        "data_dir": "data/reviews",
        "data_type": "text",
        "available_sizes": ["small", "medium", "large"],
        "preprocess": collect_sa_data,
        "process": sentiment_analysis,
    },
    "ocr": {
        "name": "Optical Character Recognition",
        "data_dir": "data/license_plates",
        "data_type": "image",
        "available_sizes": ["small", "medium", "large"],
        "preprocess": fimg_from_dir,
        "process": ocr_license_plate,
    },
    "yolo": {
        "name": "Object Detection",
        "data_dir": "data/coco128_images",
        "data_type": "image",
        "available_sizes": ["small", "medium", "large"],
        "preprocess": fimg_from_dir,
        "process": yolo_inference,
    },
}
