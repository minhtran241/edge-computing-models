# Resize image from 1.5MB to 4MB

from PIL import Image
import os

img = Image.open("./iot-edge-cloud/data/license_plates/small/KL-31-B-4000-2MB.jpg")
img = img.resize((8353 * 2, 2011 * 2))
img.save("./iot-edge-cloud/data/license_plates/small/KL-31-B-4000-2MB1.jpg")
print(
    os.path.getsize("./iot-edge-cloud/data/license_plates/small/KL-31-B-4000-2MB1.jpg")
)
