import cv2
import numpy as np
from pytesseract import image_to_string


def enlarge_img(image: np.ndarray, scale_percent: int) -> np.ndarray:
    """
    Enlarge an image by a certain percentage.

    Args:
        image (np.ndarray): The image to enlarge.
        scale_percent (int): The percentage to enlarge the image by.

    Returns:
        np.ndarray: The enlarged image.
    """
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized_image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    return resized_image


def ocr_license_plate(data: bytes) -> str:
    """
    Perform OCR on an image to extract the license plate.

    Args:
        data (bytes): The image data in bytes.

    Returns:
        str: The extracted license plate.
    """
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    carplate_extract_img = enlarge_img(img, 150)
    carplate_extract_img_gray = cv2.cvtColor(carplate_extract_img, cv2.COLOR_RGB2GRAY)
    carplate_extract_img_gray_blur = cv2.medianBlur(carplate_extract_img_gray, 3)
    return image_to_string(
        carplate_extract_img_gray_blur,
        config="--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    )
