def get_device_id(environ):
    return environ.get("HTTP_DEVICE_ID", None)
