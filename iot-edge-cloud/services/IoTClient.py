import os
import socketio
import time
import threading
from typing import Any
from dotenv import load_dotenv
from helpers.common import cal_data_size, process_data, emit_data
from . import *

load_dotenv()


class IoTClient(threading.Thread):
    def __init__(
        self,
        device_id: str,
        size_option: str,
        target_address: str,
        algo: Algorithm,
        arch: ModelArch,
        iterations: int,
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
            logger=True,
            # engineio_logger=True,
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
        time_stats = {"acc_transtime": self.transtime, "acc_proctime": self.proctime}
        self.logger.info(time_stats)
        if self.arch == ModelArch.EDGE:
            with self.lock:
                self.sio.emit("recv", time_stats)
        else:
            self.sio.emit("recv", time_stats)

    def connect_to_target(self):
        self.sio.connect(
            self.target_address,
            headers={"device_id": self.device_id},
            transports=["websocket"],
            wait=True,
            wait_timeout=10,
        )
        self.logger.info(f"Connected to target node ({self.target_address})")

    def run(self):
        try:
            self.connect_to_target()

            data_size = cal_data_size(self.data_dir)
            formatted_data = self.algo.value["preprocess"](self.data_dir)

            # Wrap the iterations loop with tqdm for progress tracking
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
        self.logger.info("Stopping IoT client...")
        self.running.clear()
        self.disconnect_from_target()

    def disconnect_from_target(self):
        self.sio.disconnect()
        self.logger.info(f"Disconnected from target node ({self.target_address}).")

    def __del__(self):
        self.stop()

    def start_in_main_thread(self):
        """
        Start the IoT client in the main thread without using threading.
        """
        self.run()
