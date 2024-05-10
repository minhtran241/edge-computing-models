from typing import Any, Union


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
