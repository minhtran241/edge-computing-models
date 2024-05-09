import os
import time
from typing import List, Dict, Any
from ultralytics import YOLO
from common import bytes_to_image


def predict_images(img_batch: List[str], model: YOLO) -> List[Dict[str, Any]]:
    """
    Predict the objects in the images using the YOLO model.

    Args:
        img_batch (List[str]): A list of image paths.
        model (YOLO): The YOLO model.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing the results of the predictions.
    """
    results = model(img_batch)
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


def yolo_inference(
    data: bytes, model: YOLO, device_id: str = "unknown"
) -> Dict[str, Any]:
    """
    Perform object detection on an image using the YOLO model.

    Args:
        data (bytes): The image data in bytes.
        model (YOLO): The YOLO model.
        device_id (str): The unique identifier of the device.

    Returns:
        Dict[str, Any]: A dictionary containing the results of the prediction.
    """
    fpath = f"recv_images/{device_id}/{int(time.time())}.jpg"
    # Create the directory if it does not exist
    os.makedirs(os.path.dirname(fpath), exist_ok=True)
    bytes_to_image(data, fpath)
    data = predict_images([fpath], model)[0]
    return data
