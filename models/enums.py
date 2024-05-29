from typing import Any, Dict
from enum import Enum
from config import DATA_CONFIG


class ModelArch(Enum):
    """
    Enum class for the architecture of the device.
    """

    IOT: str = "IoT"
    EDGE: str = "Edge"
    CLOUD: str = "Cloud"


class Algorithm(Enum):
    """
    Enum class for the algorithm to be used.
    """

    SW: Dict[str, Any] = DATA_CONFIG["sw"]
    SA: Dict[str, Any] = DATA_CONFIG["sa"]
    OCR: Dict[str, Any] = DATA_CONFIG["ocr"]
    YOLO: Dict[str, Any] = DATA_CONFIG["yolo"]
