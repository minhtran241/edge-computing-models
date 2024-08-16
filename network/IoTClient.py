import os
import socketio
import time
import threading
from typing import Any
from dotenv import load_dotenv
from constants import DEFAULT_ITERATIONS
from helpers.common import cal_data_size, process_data, emit_data
from helpers.logger import Logger
from models.enums import ModelArch, Algorithm

load_dotenv()


class IoTClient(threading.Thread):
    """
    IoT client class to send data to the targeted server nodes.

    :param device_id: The unique identifier of the IoT client.
    :type device_id: str
    :param data_dir: The directory containing the data to be sent.
    :type data_dir: Any
    :param algo: The algorithm to be used for processing the data.
    :type algo: Algorithm, optional
    :param size_option: The size option of the data.
    :type size_option: str
    :param target_address: The address of the target node.
    :type target_address: str
    :param arch: The architecture type, either IoT, 'Edge' or 'Cloud'.
    :type arch: ModelArch
    :param iterations: The number of iterations to run, defaults to DEFAULT_ITERATIONS.
    :type iterations: int, optional
    """

    def __init__(
        self,
        device_id: str,
        size_option: str,
        target_address: str,
        algo: Algorithm,
        arch: ModelArch,
        iterations: int = DEFAULT_ITERATIONS,
    ):
        super().__init__()
        self.device_id = device_id
        self.data_dir = os.path.join(algo.value["data_dir"], size_option)
        self.algo = algo
        self.size_option = size_option
        self.target_address = target_address
        self.iterations = iterations
        self.arch = arch
        self.sio = socketio.Client(
            # handle_sigint=True,
            # reconnection=False,
            logger=True,
            engineio_logger=True,
            wait=True,
            wait_timeout=10,
        )
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
                "algo": self.algo.name,
                "iterations": self.iterations,
                "arch": self.arch.name,
            }
        )

    def _format_and_send(self, data_size: int, data: Any):
        """
        Send data to the target node.

        Args:
            data_size (int): Size of the data being sent.
            data (Any): Data to be sent.
        """
        sent_data = {
            "arch": self.arch.name,
            "data_size": data_size,
            "data_dir": self.data_dir,
            "algo": self.algo.name,
            "data": data,
            "iters": self.iterations,
        }
        if self.arch == ModelArch.EDGE:
            with self.lock:
                tt = emit_data(self.sio, sent_data)
                self.transtime += tt
        else:
            tt = emit_data(self.sio, sent_data)
            self.transtime += tt

    def _emit_timestats(self):
        """
        Emit accumulated transmission and processing times to the target node.
        """
        time_stats = {"acc_transtime": self.transtime, "acc_proctime": self.proctime}
        self.logger.info(time_stats)
        if self.arch == ModelArch.EDGE:
            with self.lock:
                self.sio.emit("recv", time_stats)
        else:
            self.sio.emit("recv", time_stats)

    def connect_to_target(self):
        """
        Connect to the target node.
        """
        self.sio.connect(
            self.target_address,
            headers={"device_id": self.device_id},
            transports=["websocket"],
        )
        self.logger.info(f"Connected to target node ({self.target_address})")

    def run(self):
        """
        Run the IoT client.
        """
        try:
            self.connect_to_target()

            data_size = cal_data_size(self.data_dir)
            formatted_data = self.algo.value["preprocess"](self.data_dir)

            for _ in range(self.iterations):
                if self.arch == ModelArch.IOT:
                    result, pt = process_data(
                        func=self.algo.value["process"], data=formatted_data
                    )
                    self.proctime += pt
                    self._format_and_send(data_size, result)
                else:
                    self._format_and_send(data_size, formatted_data)

            self._emit_timestats()

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
        self.disconnect_from_target()

    def disconnect_from_target(self):
        """
        Disconnect from the target node.
        """
        self.sio.disconnect()
        self.logger.info(f"Disconnected from target node ({self.target_address}).")

    def __del__(self):
        self.stop()
