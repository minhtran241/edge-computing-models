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


import logging
from colorlog import ColoredFormatter


"""
This module contains the custom logger class for the IoT edge-cloud system.
"""


class Logger(logging.Logger):
    def __init__(self, device_id: str = "unknown", level: int = logging.DEBUG):
        super().__init__(device_id)
        self.setLevel(level)
        self._console_handler = None  # Lazy initialization of console handler
        self.addHandler(self.get_console_handler())

    def get_console_handler(self) -> logging.Handler:
        if self._console_handler is None:
            self._console_handler = self._create_console_handler()
        return self._console_handler

    @staticmethod
    def _create_console_handler() -> logging.Handler:
        formatter = ColoredFormatter(
            "%(log_color)s[%(process)s] %(threadName)s: %(levelname)-8s%(reset)s "
            "%(bg_blue)s[%(name)s]%(reset)s %(message)s",
            reset=True,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red",
            },
        )
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        return console_handler
