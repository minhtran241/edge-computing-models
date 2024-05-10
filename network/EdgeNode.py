import os
import threading
import eventlet
import socketio
import time
import queue
from typing import Any
from dotenv import load_dotenv
from helpers.logger import Logger
from config import DATA_CONFIG

load_dotenv()


class EdgeNode:
    """
    Edge node class to process data from IoT devices and send it to the cloud.
    """

    def __init__(
        self,
        device_id: str,
        port: int = 10000,
        cloud_addr: str = os.getenv("CLOUD_ADDRESS") or "http://localhost:20000",
    ):
        """
        Initialize the EdgeNode instance.

        Args:
            device_id (str): The unique identifier of the edge node.
            port (int, optional): The port on which the edge node will run. Defaults to 10000.
            cloud_addr (str, optional): The address of the cloud server. Defaults to CLOUD_ADDRESS.
        """
        self.device_id = device_id
        self.cloud_addr = cloud_addr
        self.port = port
        self.sio_client = socketio.Client()
        self.sio_server = socketio.Server()
        self.app = socketio.WSGIApp(self.sio_server)
        self.logger = Logger(name=f"EdgeNode-{device_id}").get_logger()
        self.queue = queue.Queue()
        self.transtime = 0
        self.proctime = 0
        self.running = threading.Event()

    def process_iot_data(self):
        """
        Process the data received from IoT devices.
        """
        while self.running.is_set():
            try:
                device_id, data = self.queue.get(timeout=1)
                self._process_iot_data(device_id, data)
                self.queue.task_done()
            except queue.Empty:
                pass

    def _process_iot_data(self, device_id: str, data: Any):
        """
        Process the data received from an IoT device.

        Args:
            device_id (str): The identifier of the IoT device.
            data (Any): The data received from the IoT device.
        """
        # Sample: data = {"fsize": fsize, "fpath": fpath, "data": formatted, "algo": algo}
        recv_data = data["data"]
        algo = data["algo"]

        start_time = time.time()
        result = DATA_CONFIG[algo]["process"](recv_data)
        self.proctime += time.time() - start_time

        # Remain attributes the same, just change the data to the result and the device_id of the IoT device
        sent_data = {
            "fsize": data["fsize"],
            "fpath": data["fpath"],
            "algo": algo,
            "data": result,
            "iot_device_id": device_id,
        }

        start_time = time.time()
        self.sio_client.emit(
            "recv",
            data=sent_data,
        )
        self.transtime += time.time() - start_time

        self.sio_client.emit(
            "recv",
            data={
                "transtime": self.transtime,
                "proctime": self.proctime,
            },
        )

    def run(self):
        """
        Run the edge node.
        """
        try:
            self.running.set()
            pidt = threading.Thread(target=self.process_iot_data, daemon=True)
            pidt.start()
            self.sio_client.connect(
                self.cloud_addr, headers={"device_id": self.device_id}
            )
            self.logger.info(f"Connected to cloud ({self.cloud_addr})")
            eventlet.wsgi.server(eventlet.listen(("", self.port)), self.app)
        except Exception as e:
            pidt.join()
            self.logger.error(f"An error occurred: {e}")

    def stop(self):
        """
        Stop the edge node gracefully.
        """
        self.running.clear()
        self.sio_client.disconnect()
        self.sio_server.stop()
