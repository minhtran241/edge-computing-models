import os
import time
from typing import List, Dict, Any, Union
from ultralytics import YOLO
from helpers.common import bytes_to_image


def _predict_images(
    img_batch: Union[List[str], str],
    model: YOLO = YOLO(model=os.getenv("YOLOV8_MODEL_PATH") or "yolov8m.pt"),
) -> List[Dict[str, Any]]:
    """
    Predict the objects in the images using the YOLO model.

    Args:
        img_batch (Union[List[str], str]): The image batch to predict.
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


def yolo_inference(data: bytes) -> Dict[str, Any]:
    """
    Perform object detection on an image using the YOLO model.

    Args:
        data (bytes): The image data in bytes.
        model (YOLO): The YOLO model.
        device_id (str): The unique identifier of the device.

    Returns:
        Dict[str, Any]: A dictionary containing the results of the prediction.
    """
    data_dir = f"recv_images/{int(time.time())}.jpg"
    # Create the directory if it does not exist
    os.makedirs(os.path.dirname(data_dir), exist_ok=True)
    bytes_to_image(data, data_dir)
    data = _predict_images(data_dir)[0]
    return data
