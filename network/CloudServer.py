import eventlet
import socketio
import queue
import threading
import pandas as pd
from typing import Any
from dotenv import load_dotenv
from helpers.common import get_device_id
from helpers.abstract import process_data
from helpers.logger import Logger
from tabulate import tabulate

load_dotenv()


class CloudServer:
    """
    Cloud server class to receive processed data from edge nodes.
    """

    def __init__(self, device_id: str, port: int = 20000, arch: str = "Edge"):
        """
        Initialize the CloudServer instance.

        Args:
            device_id (str): The unique identifier for the device.
            port (int, optional): The port on which the cloud server will run. Defaults to 20000.
            arch (str, optional): The architecture type, either 'Edge' or 'Cloud'. Defaults to 'Edge'.
        """
        self.device_id = device_id
        self.port = port
        self.arch = arch
        self.sio = socketio.Server(always_connect=True)
        self.app = socketio.WSGIApp(self.sio)
        self.logger = Logger(self.device_id)
        self.queue = queue.Queue()
        self.data = {}
        self.transtimes = {}
        self.proctimes = {}
        self.logger.info(
            {"device_id": self.device_id, "port": self.port, "arch": self.arch}
        )

    def process_recv_data(self):
        """
        Process the received data from IoT devices.
        """
        while True:
            try:
                device_id, data = self.queue.get(timeout=1)
                result, pt = process_data(data["data"], data["algo"])
                self.queue.task_done()
                with threading.Lock():
                    self.proctimes[device_id] += pt
                    self.logger.info(f"Processed data from node {device_id}: {result}")
                    self.data.setdefault(device_id, []).append(
                        {
                            "data_size": data["data_size"],
                            "data_dir": data["data_dir"],
                            "algo": data["algo"],
                            "data": result,
                            "iot_device_id": device_id,
                        }
                    )
            except queue.Empty:
                continue

    def print_stats(self):
        """
        Print the statistics for all edge nodes.
        """
        df = pd.DataFrame(
            {
                "Device ID": list(self.transtimes.keys()),
                "Files Received": [
                    len(self.data.get(device_id, [])) for device_id in self.data
                ],
                "Total File Size": [
                    sum(d["data_size"] for d in self.data.get(device_id, []))
                    for device_id in self.data
                ],
                "Transmission Time": list(self.transtimes.values()),
                "Processing Time": list(self.proctimes.values()),
            }
        )
        print(tabulate(df, headers="keys", tablefmt="pretty", showindex=False))

    def run_server(self):
        """
        Run the cloud server.
        """
        try:
            eventlet.wsgi.server(eventlet.listen(("", self.port)), self.app)
        except Exception as e:
            self.logger.error(f"An error occurred while running the server: {e}")

    def run(self):
        """
        Start the cloud server and set up event handlers.
        """
        server_thread = eventlet.spawn(self.run_server)

        @self.sio.event
        def connect(sid, environ):
            device_id = get_device_id(environ) or sid
            self.sio.save_session(sid, {"device_id": device_id})
            self.logger.info(f"Edge node {device_id} connected, session ID: {sid}")

        @self.sio.event
        def disconnect(sid):
            session = self.sio.get_session(sid)
            device_id = session["device_id"]
            self.logger.info(f"Node {device_id} disconnected")

        @self.sio.event
        def recv(sid, data):
            session = self.sio.get_session(sid)
            device_id = session["device_id"]
            self.data.setdefault(device_id, [])
            self.transtimes.setdefault(device_id, 0)
            self.proctimes.setdefault(device_id, 0)

            if "data" in data and data["data"] is not None:
                if self.arch == "Cloud":
                    self.logger.info(f"Received data from node {device_id}")
                    self.queue.put((device_id, data))
                else:
                    self.logger.info(f"Result from node {device_id}: {data}")
                    self.data[device_id].append(data)
                self.logger.info(
                    f"Files received from node {device_id}: {len(self.data[device_id])}"
                )
            elif "acc_transtime" in data and "acc_proctime" in data:
                self.transtimes[device_id] += data["acc_transtime"]
                self.proctimes[device_id] += data["acc_proctime"]

        if self.arch == "Cloud":
            threading.Thread(target=self.process_recv_data, daemon=True).start()

        server_thread.wait()

    def stop(self):
        """
        Stop the cloud server.
        """
        self.logger.info("Stopping cloud server...")
        self.sio.shutdown()
