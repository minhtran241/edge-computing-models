import os
import socketio
import time
import threading
from typing import Any
from dotenv import load_dotenv
from constants import DEFAULT_ITERATIONS
from config import DATA_CONFIG
from helpers.abstract import process_data, send_data
from helpers.logger import Logger

load_dotenv()


class IoTClient(threading.Thread):
    """
    IoT client class to send data to edge nodes.
    """

    def __init__(
        self,
        device_id: str,
        data_dir: Any,
        algo: str,
        size_option: str,
        target_address: str,
        iterations: int = DEFAULT_ITERATIONS,
        arch: str = "Edge",
    ):
        """
        Initializes the IoTClient object.

        Args:
            device_id (str): The unique identifier of the IoT device.
            target_address (str): The address of the edge node.
        """
        super().__init__()
        self.device_id = device_id
        self.target_address = target_address
        self.data_dir = os.path.join(data_dir, size_option)
        self.algo = algo
        self.arch = arch
        self.iterations = iterations
        self.sio = socketio.Client(handle_sigint=True, reconnection=True, logger=True)
        self.transtime = 0  # Transmission time
        self.proctime = 0  # Processing time
        self.logger = Logger(self.device_id)
        self.running = threading.Event()  # Event to control the client's running state
        self.running.set()  # Set the event to True initially
        self.lock = threading.Lock()  # Lock to ensure thread safety
        self.logger.info(
            {
                "device_id": self.device_id,
                "target_address": self.target_address,
                "data_dir": self.data_dir,
                "algo": self.algo,
                "iterations": self.iterations,
                "arch": self.arch,
            }
        )

    def send(self, data_size: int, data: Any):
        """
        Sends data to edge nodes.
        """
        for _ in range(self.iterations):
            sent_data = {
                "data_size": data_size,
                "data_dir": self.data_dir,
                "algo": self.algo,
                "data": data,
            }
            with self.lock:
                tt = send_data(self.sio, sent_data)
                self.transtime += tt

        with self.lock:
            self.sio.emit(
                "recv",
                data={"acc_transtime": self.transtime, "acc_proctime": self.proctime},
            )

    def run(self):
        """
        Runs the IoT client.
        """
        try:
            self.sio.connect(
                self.target_address,
                headers={"device_id": self.device_id},
                transports=["websocket"],
            )
            self.logger.info(f"Connected to edge node ({self.target_address})")
            data_size = sum(
                os.path.getsize(os.path.join(self.data_dir, f))
                for f in os.listdir(self.data_dir)
            )
            formatted = DATA_CONFIG[self.algo]["preprocess"](self.data_dir)

            if self.arch == "IoT":
                result, pt = process_data(formatted, self.algo)
                self.proctime += pt
                self.send(data_size, result)
            else:
                self.send(data_size, formatted)

            while self.running.is_set():
                time.sleep(1)
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")

    def stop(self):
        """
        Stops the IoT client gracefully.
        """
        self.logger.info("Stopping IoT client...")
        self.running.clear()
        self.disconnect_from_edge()

    def disconnect_from_edge(self):
        """
        Disconnects from the edge node.
        """
        self.sio.disconnect()
        self.logger.info(f"Disconnected from edge node ({self.target_address}).")

    def __del__(self):
        self.stop()
