import os
import re
from typing import List, Dict, Any
from ultralytics import YOLO


def get_device_id(environ: Any) -> str:
    """
    Get the device ID from the environment variables.

    Args:
        environ (Any): The environment variables.

    Returns:
        str: The device ID.
    """
    return environ.get("HTTP_DEVICE_ID", None)


def count_word_occurrences(input_string: str, word: str) -> int:
    return sum(1 for _ in re.finditer(r"\b%s\b" % re.escape(word), input_string))


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


# Each edge node is raspberry pi 4 so for processing YOLO, 3.1 FPS is a good value. This function will have default batch size of 3 be
def get_img_batches(
    dir: str, num_parts: int, max_batch_size: int
) -> List[List[List[str]]]:
    """
    Split the images in the directory into multiple batches for each edge node.

    Args:
        dir (str): The directory containing the images.
        num_parts (int): The number of edge nodes.
        max_batch_size (int): The maximum number of images in each batch.

    Returns:
        List[List[List[str]]]: A list of edge nodes, each containing a list of batches, each containing a list of image paths.
    """
    # Get all image paths in the directory
    img_paths = [
        os.path.join(dir, img) for img in os.listdir(dir) if img.endswith(".jpg")
    ]
    # Split the image paths into num_parts parts, each part have multiple batches, each batch has max_batch_size images
    # Sample output: [[[img1, img2], [img1, img2]], [[img1, img2], [img1, img2]], [[img1, img2], [img1, img2]]]
    # If there are remaining images, add them to the random part (create a new batch for those images)

    data_parts = [[] for _ in range(num_parts)]
    for i, img_path in enumerate(img_paths):
        part_idx = i % num_parts
        if (
            len(data_parts[part_idx]) == 0
            or len(data_parts[part_idx][-1]) == max_batch_size
        ):
            data_parts[part_idx].append([])
        data_parts[part_idx][-1].append(img_path)

    # print the number of images in each part, each batch, and the total number of images
    for i, part in enumerate(data_parts):
        print(f"Part {i}:")
        for j, batch in enumerate(part):
            print(f"  Batch {j}: {len(batch)} images")
        print(f"Total: {sum(len(batch) for batch in part)} images")
    return data_parts
