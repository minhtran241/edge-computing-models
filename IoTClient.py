import os
import socketio
import time
from typing import List, Any
from threading import Thread, Lock, Event
from utils.constants import EDGE_NODE_ADDRESSES, IMAGE_DIR
from utils.helper_functions import partition_images, image_to_bytes
from Logger import Logger


class IoTClient(Thread):
    """
    Class representing an IoT client that sends data to edge nodes.

    Attributes:
        device_id (str): The unique identifier of the IoT device.
        edge_address (str): Address of the edge node.
        sio (socketio.Client): Socket.IO client instance.
        logger (Logger): Logger instance for logging.

    Methods:
        __init__: Initializes the IoTClient object.
        send: Sends data to edge nodes.
        run: Runs the IoT client.
        stop_client: Stops the IoT client gracefully.
        disconnect_from_edge: Disconnects from the edge node.
    """

    def __init__(self, device_id: str, edge_address: str, data: Any):
        """
        Initializes the IoTClient object.

        Args:
            device_id (str): The unique identifier of the IoT device.
            edge_address (str): The address of the edge node.
        """
        super().__init__()
        self.device_id = device_id
        self.edge_address = edge_address
        self.data = data
        self.sio = socketio.Client()  # Socket.IO client
        self.transtime = (
            0  # Transmission time from IoT device to edge node (accumulated)
        )
        self.logger = Logger(name=f"IoTClient-{device_id}").get_logger()
        self.running = Event()  # Event to control the client's running state
        self.running.set()  # Set the event to True initially
        self.lock = Lock()  # Lock to ensure thread safety

    def send(self):
        """
        Sends data to edge nodes.
        """
        for img_path in self.data:
            fsize = os.path.getsize(img_path)
            img_data = image_to_bytes(img_path)
            with self.lock:
                start_time = time.time()
                self.sio.emit("recv", data={"fsize": fsize, "data": img_data})
                self.transtime += time.time() - start_time

        with self.lock:
            self.sio.emit("recv", data={"acc_transtime": self.transtime})

    def run(self):
        """
        Runs the IoT client.
        """
        try:
            self.sio.connect(self.edge_address, headers={"device_id": self.device_id})
            self.logger.info(f"Connected to edge node ({self.edge_address})")
            self.send()
            self.sio.wait()
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")

    def stop_client(self):
        """
        Stops the IoT client gracefully.
        """
        self.running.clear()
        self.disconnect_from_edge()
        self.logger.info("IoT client stopped.")

    def disconnect_from_edge(self):
        """
        Disconnects from the edge node.
        """
        self.sio.disconnect()
        self.logger.info(f"Disconnected from edge node ({self.edge_address}).")

    def __del__(self):
        self.stop_client()


if __name__ == "__main__":
    try:
        data = partition_images(dir=IMAGE_DIR, num_parts=len(EDGE_NODE_ADDRESSES))
        iot_clients: List[IoTClient] = []
        for i, edge_address in enumerate(EDGE_NODE_ADDRESSES):
            iot_client = IoTClient(
                device_id=f"iot-{i+1}",
                edge_address=edge_address,
                data=data[i],
            )
            iot_clients.append(iot_client)
            iot_client.start()

        for iot_client in iot_clients:
            iot_client.join()
    except (KeyboardInterrupt, SystemExit, Exception) as e:
        if isinstance(e, Exception):
            print(f"An error occurred: {e}")
        for iot_client in iot_clients:
            iot_client.stop_client()
        print("IoT clients stopped.")
