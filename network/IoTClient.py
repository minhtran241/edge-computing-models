import os
import socketio
import time
import threading
from typing import Any
from constants import ITERATIONS
from config import DATA_CONFIG
from helpers.logger import Logger
from dotenv import load_dotenv

load_dotenv()


class IoTClient(threading.Thread):
    """
    IoT client class to send data to edge nodes.
    """

    def __init__(
        self,
        device_id: str,
        edge_address: str,
        data: Any,
        algo: str,
        iterations: int = ITERATIONS,
    ):
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
        self.algo = algo
        self.iterations = iterations
        self.sio = socketio.Client()  # Socket.IO client
        self.transtime = (
            0  # Transmission time from IoT device to edge node (accumulated)
        )
        self.logger = Logger(name=f"IoTClient-{device_id}").get_logger()
        self.running = threading.Event()  # Event to control the client's running state
        self.running.set()  # Set the event to True initially
        self.lock = threading.Lock()  # Lock to ensure thread safety

    def send(self):
        """
        Sends data to edge nodes.
        """
        fsize = os.path.getsize(self.data)
        formatted = DATA_CONFIG[self.algo]["preprocess"](self.data)

        for _ in range(self.iterations):

            sent_data = {
                "fsize": fsize,
                "fpath": self.data,
                "algo": self.algo,
                "data": formatted,
            }

            with self.lock:
                start_time = time.time()
                self.sio.emit("recv", data=sent_data)
                self.transtime += time.time() - start_time

        with self.lock:
            self.sio.emit(
                "recv",
                data={"acc_transtime": self.transtime},
            )

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
