import os
from typing import List, Any, Union


def get_device_id(environ: Any) -> str:
    """
    Get the device ID from the environment variables.

    Args:
        environ (Any): The environment variables.

    Returns:
        str: The device ID.
    """
    return environ.get("HTTP_DEVICE_ID", None)


def partition_images(dir: str, num_parts: int) -> List[List[str]]:
    """
    Split the images in the directory into multiple parts for each edge node.

    Args:
        dir (str): The directory containing the images.
        num_parts (int): The number of edge nodes.

    Returns:
        List[List[str]]: A list of edge nodes, each containing a list of image paths.
    """
    # Get all image paths in the directory
    img_paths = [
        os.path.join(dir, img) for img in os.listdir(dir) if img.endswith(".jpg")
    ]
    # Split the image paths into num_parts parts
    data_parts = [[] for _ in range(num_parts)]
    for i, img_path in enumerate(img_paths):
        data_parts[i % num_parts].append(img_path)
    return data_parts


def image_to_bytes(filename: Union[str, bytes]) -> bytes:
    """
    Convert an image to bytes.

    Args:
        filename (str | bytes): The path to the image file or the image data in bytes.

    Returns:
        bytes: The image data in bytes.
    """
    with open(filename, "rb") as f:
        return f.read()


def bytes_to_image(data: bytes, save_path: str):
    """
    Convert bytes to an image and save it to a file.

    Args:
        data (bytes): The image data in bytes.
        save_path (str): The path to save the image.
    """
    with open(save_path, "wb") as f:
        f.write(data)
