import os
from typing import Any, Union, List
from constants import VALID_ROLES


def get_nid(role: str, id: int = 0) -> str:
    """
    Get the network ID based on the role and ID (i0 for IoT, e0 for edge, c0 for cloud)

    Args:
        role (str): The role of the node.
        id (int): The ID of the node.

    Returns:
        str: The node ID.
    """
    if role not in VALID_ROLES:
        raise ValueError(f"Invalid role: {role}. Valid roles are: {VALID_ROLES}")
    return f"{role[0]}{id}"


def get_device_id(environ: Any) -> str:
    """
    Get the device ID from the environment variables.

    Args:
        environ (Any): The environment variables.

    Returns:
        str: The device ID.
    """
    return environ.get("HTTP_DEVICE_ID", None)


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


def read_txt(filename: str) -> str:
    """
    Read the text data from the specified file.

    Args:
        filename (str): The file containing the text data.

    Returns:
        str: The text data read from the file.
    """
    with open(filename, "r") as f:
        txt = f.read()
    return txt


def read_txt_lines(filename: str) -> List[str]:
    """
    Read the lines of text data from the specified file.

    Args:
        filename (str): The file containing the text data.

    Returns:
        List[str]: The lines of text data read from the file.
    """
    with open(filename, "r") as f:
        lines = f.readlines()
    return [line.strip() for line in lines]


def fimg_from_dir(dir: str, out_format: str = "bytes") -> Any:
    """
    Get the first image from the specified directory.

    Args:
        dir (str): The directory containing the images.
        out_format (str): The output format ("bytes" or "path").

    Returns:
        Any: The image data in bytes or the path to the image file.
    """
    img_files = [f for f in os.listdir(dir) if f.endswith((".jpg", ".jpeg", ".png"))]
    if not img_files:
        raise ValueError(f"No image files found in the directory: {dir}")
    img_file = img_files[0]
    img_path = os.path.join(dir, img_file)
    if out_format == "bytes":
        return image_to_bytes(img_path)
    elif out_format == "path":
        return img_path
    else:
        raise ValueError(
            f"Invalid output format: {out_format}. Valid formats are: 'bytes', 'path'"
        )


def cal_data_size(dir: str) -> int:
    """
    Calculate the total size of data in the data directory.

    Returns:
        int: Total size of data.
    """
    return sum(os.path.getsize(os.path.join(dir, f)) for f in os.listdir(dir))
