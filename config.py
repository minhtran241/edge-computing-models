from typing import Dict
from helpers.common import fimg_from_dir
from helpers.ocr import ocr_license_plate
from helpers.yolo import yolo_inference
from helpers.sw import records_to_txt, smith_waterman
from helpers.sa import read_reviews, sentiment_analysis

DATA_CONFIG: Dict[str, Dict[str, str]] = {
    "sw": {
        "name": "Smith-Waterman",
        "data_dir": "data/hsa/small",
        "data_type": "text",
        "preprocess": records_to_txt,
        "process": smith_waterman,
    },
    "sa": {
        "name": "Sentiment Analysis",
        "data_dir": "data/reviews",
        "data_type": "text",
        "preprocess": read_reviews,
        "process": sentiment_analysis,
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
