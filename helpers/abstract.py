import time
import socketio
from typing import Any, Tuple
from config import DATA_CONFIG


def process_data(data: Any, algo: str) -> Tuple[Any, float]:
    try:
        start_time = time.time()
        result = DATA_CONFIG[algo]["process"](data)
        proctime = time.time() - start_time

        # Remain attributes the same, just change the data to the result and the device_id of the IoT device
        return result, proctime
    except Exception as e:
        raise e


def send_data(sio: socketio.Client, data: Any) -> float:
    try:
        start_time = time.time()
        sio.emit("recv", data=data)
        transtime = time.time() - start_time
        return transtime
    except Exception as e:
        raise e
