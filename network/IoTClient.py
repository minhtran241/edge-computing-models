import os
import socketio
import time
import threading
from typing import Any
from dotenv import load_dotenv
from constants import DEFAULT_ITERATIONS
from config import DATA_CONFIG
from helpers.abstract import process_data, send_data
from helpers.common import cal_data_size
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
            data_dir (Any): The directory where data is stored.
            algo (str): The algorithm to use.
            size_option (str): The size option for data.
            target_address (str): The address of the edge node.
            iterations (int, optional): The number of iterations. Defaults to DEFAULT_ITERATIONS.
            arch (str, optional): The architecture type, either 'IoT' or 'Edge'. Defaults to 'Edge'.
        """
        super().__init__()
        self.device_id = device_id
        self.data_dir = os.path.join(data_dir, size_option)
        self.algo = algo
        self.size_option = size_option
        self.target_address = target_address
        self.iterations = iterations
        self.arch = arch
        self.sio = socketio.Client(handle_sigint=True, reconnection=True, logger=True)
        self.transtime = 0
        self.proctime = 0
        self.logger = Logger(self.device_id)
        self.running = threading.Event()
        self.running.set()
        self.lock = threading.Lock()
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

    def _format_and_send(self, data_size: int, data: Any):
        """
        Send data to the edge node.

        Args:
            data_size (int): Size of the data being sent.
            data (Any): Data to be sent.
        """
        sent_data = {
            "data_size": data_size,
            "data_dir": self.data_dir,
            "algo": self.algo,
            "data": data,
        }
        if self.arch == "IoT":
            with self.lock:
                tt = send_data(self.sio, sent_data)
                self.transtime += tt
        else:
            tt = send_data(self.sio, sent_data)
            self.transtime += tt

    def _emit_statistics(self):
        """
        Emit accumulated transmission and processing times to the edge node.
        """
        if self.arch == "IoT":
            with self.lock:
                self.sio.emit(
                    "recv",
                    {"acc_transtime": self.transtime, "acc_proctime": self.proctime},
                )
        else:
            self.sio.emit(
                "recv", {"acc_transtime": self.transtime, "acc_proctime": self.proctime}
            )

    def connect_to_edge_node(self):
        """
        Connect to the edge node.
        """
        self.sio.connect(
            self.target_address,
            headers={"device_id": self.device_id},
            transports=["websocket"],
        )
        self.logger.info(f"Connected to edge node ({self.target_address})")

    def run(self):
        """
        Run the IoT client.
        """
        try:
            self.connect_to_edge_node()

            data_size = cal_data_size(self.data_dir)
            formatted_data = DATA_CONFIG[self.algo]["preprocess"](self.data_dir)

            for _ in range(self.iterations):
                if self.arch == "IoT":
                    result, pt = process_data(formatted_data, self.algo)
                    self.proctime += pt
                    self._format_and_send(data_size, result)
                else:
                    self._format_and_send(data_size, formatted_data)

            self._emit_statistics()

            while self.running.is_set():
                time.sleep(1)

        except Exception as e:
            self.logger.error(f"An error occurred: {e}")

    def stop(self):
        """
        Stop the IoT client gracefully.
        """
        self.logger.info("Stopping IoT client...")
        self.running.clear()
        self.disconnect_from_edge_node()

    def disconnect_from_edge_node(self):
        """
        Disconnect from the edge node.
        """
        self.sio.disconnect()
        self.logger.info(f"Disconnected from edge node ({self.target_address}).")

    def __del__(self):
        self.stop()
