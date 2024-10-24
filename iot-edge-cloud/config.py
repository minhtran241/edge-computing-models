from typing import Dict
from helpers.common import fimg_from_dir
from helpers.ocr import ocr_license_plate
from helpers.sw import collect_sw_data, smith_waterman
from helpers.sa import collect_sa_data, sentiment_analysis

DATA_CONFIG: Dict[str, Dict[str, str]] = {
    "sw": {
        "name": "Smith-Waterman",
        "data_dir": "iot-edge-cloud/data/seq_align",
        "data_type": "text",
        "avail_sizes": ["small", "medium", "large"],
        "preprocess": collect_sw_data,
        "process": smith_waterman,
    },
    "sa": {
        "name": "Sentiment Analysis",
        "data_dir": "iot-edge-cloud/data/reviews",
        "data_type": "text",
        "avail_sizes": ["small", "medium", "large"],
        "preprocess": collect_sa_data,
        "process": sentiment_analysis,
    },
    "ocr": {
        "name": "Optical Character Recognition",
        "data_dir": "iot-edge-cloud/data/license_plates",
        "data_type": "image",
        "avail_sizes": ["small", "medium", "large"],
        "preprocess": fimg_from_dir,
        "process": ocr_license_plate,
    },
}
