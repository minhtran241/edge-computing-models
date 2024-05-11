import os
import socketio
import time
import threading
from typing import Any
from dotenv import load_dotenv
from constants import ITERATIONS
from config import DATA_CONFIG
from helpers.logger import Logger

load_dotenv()


class IoTClient(threading.Thread):
    """
    IoT client class to send data to edge nodes.
    """

    def __init__(
        self,
        device_id: str,
        edge_address: str,
        data_dir: Any,
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
        self.data_dir = data_dir
        self.algo = algo
        self.iterations = iterations
        self.sio = socketio.Client()  # Socket.IO client
        self.transtime = 0  # Transmission time to edge node (accumulated)
        self.logger = Logger(self.device_id)
        self.running = threading.Event()  # Event to control the client's running state
        self.running.set()  # Set the event to True initially
        self.lock = threading.Lock()  # Lock to ensure thread safety
        self.logger.info(
            {
                "device_id": self.device_id,
                "edge_address": self.edge_address,
                "data_dir": self.data_dir,
                "algo": self.algo,
                "iterations": self.iterations,
            }
        )

    def send(self):
        """
        Sends data to edge nodes.
        """
        # Total file size of the data directory
        data_size = sum(
			os.path.getsize(os.path.join(self.data_dir, f))
			for f in os.listdir(self.data_dir)
		)
        formatted = DATA_CONFIG[self.algo]["preprocess"](self.data_dir)

        for _ in range(self.iterations):

            sent_data = {
                "data_size": data_size,
                "data_dir": self.data_dir,
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
