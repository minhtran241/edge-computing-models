import os
import re
from typing import List, Dict, Any
from ultralytics import YOLO


def get_device_id(environ):
    return environ.get("HTTP_DEVICE_ID", None)


def count_word_occurrences(input_string: str, word: str) -> int:
    return sum(1 for _ in re.finditer(r"\b%s\b" % re.escape(word), input_string))


def predict_images(img_paths: List[str], model: YOLO) -> List[Dict[str, Any]]:
    results = model(img_paths)
    return [
        {
            "names": res.names,
            "orig_shape": res.orig_shape,
            "path": res.path,
            "save_dir": res.save_dir,
            "speed": res.speed,
        }
        for res in results
    ]


def get_img_batches(dir: str, num_batches: int) -> List[List[str]]:
    # Get all image paths in the directory
    img_paths = [
        os.path.join(dir, img) for img in os.listdir(dir) if img.endswith(".jpg")
    ]
    # Split the image paths into num_batches batches, each containing len(img_paths) // num_batches elements
    return [
        img_paths[i : i + len(img_paths) // num_batches]
        for i in range(0, len(img_paths), len(img_paths) // num_batches)
    ]
