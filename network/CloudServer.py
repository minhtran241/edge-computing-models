import eventlet
import socketio
import queue
import threading
import pandas as pd
from typing import Any
from dotenv import load_dotenv
from tabulate import tabulate
from helpers.common import get_device_id, process_data
from helpers.logger import Logger
from helpers.models import ModelArch

load_dotenv()


class CloudServer:
    """
    Cloud server class to receive processed data from client nodes.

    :param device_id: The unique identifier of the cloud server.
    :type device_id: str
    :param port: The port on which the cloud server will run, defaults to 20000.
    :type port: int, optional
    :param arch: The architecture type, either 'Edge' or 'Cloud', defaults to ModelArch.EDGE.
    :type arch: Any, optional
    """

    def __init__(self, device_id: str, port: int = 20000, arch: Any = ModelArch.EDGE):
        self.device_id = device_id
        self.port = port
        self.arch = arch
        self.sio = socketio.Server(always_connect=True)
        self.app = socketio.WSGIApp(self.sio)
        self.logger = Logger(self.device_id)
        self.queue = queue.Queue()
        self.data = {}
        self.num_recv_packets = 0
        self.num_proc_packets = 0
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
                algo = data["algo"]
                recv_data = data["data"]
                result, pt = process_data(func=algo["process"], data=recv_data)
                self.queue.task_done()
                self.num_proc_packets += 1
                self.logger.info(
                    f"Processed data from node {device_id}: {result}. Total number of packets processed: {self.num_proc_packets}."
                )
                with threading.Lock():
                    self.proctimes[device_id] += pt
                    self.data.setdefault(device_id, []).append(
                        {
                            "arch": data["arch"],
                            "data_size": data["data_size"],
                            "data_dir": data["data_dir"],
                            "algo": algo["name"],
                            "data": result,
                            "iot_device_id": device_id,
                        }
                    )
            except queue.Empty:
                continue

    def print_stats(self):
        """
        Print the statistics for all client nodes.
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
            self.logger.info(f"Client node {device_id} connected, session ID: {sid}")

        @self.sio.event
        def disconnect(sid):
            session = self.sio.get_session(sid)
            device_id = session["device_id"]
            self.logger.info(f"Client node {device_id} disconnected")

        @self.sio.event
        def recv(sid, data):
            session = self.sio.get_session(sid)
            device_id = session["device_id"]
            self.data.setdefault(device_id, [])
            self.transtimes.setdefault(device_id, 0)
            self.proctimes.setdefault(device_id, 0)

            if "data" in data and data["data"] is not None:
                if self.arch == ModelArch.CLOUD:
                    self.logger.info(f"Received data from client node {device_id}")
                    self.queue.put((device_id, data))
                else:
                    self.logger.info(f"Result from client node {device_id}: {data}")
                    self.data[device_id].append(data)
                self.num_recv_packets += 1
                self.logger.info(f"Number of packets received: {self.num_recv_packets}")
            elif "acc_transtime" in data and "acc_proctime" in data:
                self.transtimes[device_id] += data["acc_transtime"]
                self.proctimes[device_id] += data["acc_proctime"]

        if self.arch == ModelArch.CLOUD:
            threading.Thread(target=self.process_recv_data, daemon=True).start()

        server_thread.wait()

    def stop(self):
        """
        Stop the cloud server.
        """
        self.logger.info("Stopping cloud server...")
        self.sio.shutdown()
