from typing import Any, Union
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
