import os
import threading
import eventlet
import socketio
import queue
from typing import Any
from dotenv import load_dotenv
from . import *
from helpers.common import get_device_id, process_data, emit_data, readf, writef

load_dotenv()
EDGE_LOG_DIR: str = os.getenv("EDGE_LOG_DIR", "edge_logs")

class EdgeNode:
    """
    Edge node class to process data from IoT devices and send it to the cloud.
    """

    def __init__(self, device_id: str, port: int = 10000, job: str = "recv"):
        """
        Initialize the EdgeNode instance.

        Args:
            device_id (str): The unique identifier of the edge node.
            port (int, optional): The port on which the edge node will run. Defaults to 10000.
            job (str, optional): The job of the edge node, either 'recv' or 'send'. Defaults to 'recv'.
        """
        self.device_id = device_id
        self.port = port
        self.job = job
        self.cloud_addr = os.getenv("EDGE_TARGET") if job == "send" else None
        self.sio_client = socketio.Client(logger=True)
        self.sio_server = socketio.Server(
            always_connect=True,
            max_http_buffer_size=10**8,
            monitor_clients=False,
            ping_interval=10**8,
            http_compression=False,
        )
        self.app = socketio.WSGIApp(self.sio_server)
        self.logger = Logger(self.device_id)
        self.queue = queue.Queue()
        self.transtime = 0
        self.proctime = 0
        self.iters = 0
        self.num_proc_packets = 0
        self.running = threading.Event()
        self.logger.info({
            "device_id": self.device_id,
            "port": self.port,
            "cloud_addr": self.cloud_addr,
            "job": self.job,
        })

    def process_iot_data(self):
        """
        Process the data received from IoT devices.
        """
        while self.running.is_set():
            try:
                device_id, data = self.queue.get(timeout=1)
                sent_data = self._process_iot_data(device_id, data)
                self.queue.task_done()
                self.num_proc_packets += 1
                if self.num_proc_packets == self.iters:
                    time_stats = {
                        "acc_transtime": self.transtime,
                        "acc_proctime": self.proctime,
                    }
                    writef(f"{EDGE_LOG_DIR}/time_stats.txt", time_stats)
                    writef(f"{EDGE_LOG_DIR}/sent_data.txt", sent_data)
            except queue.Empty:
                pass

    def _process_iot_data(self, device_id: str, data: Any) -> dict:
        """
        Process the data received from an IoT device.

        Args:
            device_id (str): The identifier of the IoT device.
            data (Any): The data received from the IoT device.

        Returns:
            dict: The processed data.
        """
        recv_data = data["data"]
        algo = Algorithm[data["algo"]]

        result, pt = process_data(func=algo.value["process"], data=recv_data)
        self.proctime += pt

        sent_data = {
            "arch": data["arch"],
            "data_size": data["data_size"],
            "data_dir": data["data_dir"],
            "algo": data["algo"],
            "data": result,
            "iot_device_id": device_id,
        }

        return sent_data

    def emit_data_to_cloud(self):
        """
        Emit the processed data to the cloud server.
        """
        sent_data = readf(f"{EDGE_LOG_DIR}/sent_data.txt")
        for _ in range(self.iters):
            tt = emit_data(self.sio_client, sent_data)
            self.transtime += tt
        
        time_stats = readf(f"{EDGE_LOG_DIR}/time_stats.txt")
        self.logger.info(time_stats)
        self.sio_client.emit("recv", data=time_stats)

    def run_server(self):
        """
        Run the edge node server.
        """
        try:
            eventlet.wsgi.server(eventlet.listen(("", self.port)), self.app)
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")

    def run(self):
        """
        Run the edge node.
        """
        server_thread = eventlet.spawn(self.run_server)

        @self.sio_server.event
        def connect(sid, environ):
            device_id = get_device_id(environ) or sid
            self.sio_server.save_session(sid, {"device_id": device_id})
            self.logger.info(f"IoT device {device_id} connected, session ID: {sid}")

        @self.sio_server.event
        def disconnect(sid):
            session = self.sio_server.get_session(sid)
            device_id = session["device_id"]
            self.logger.info(f"IoT device {device_id} disconnected")

        @self.sio_server.event
        def recv(sid, data):
            session = self.sio_server.get_session(sid)
            device_id = session["device_id"]
            if "data" in data and data["data"] is not None:
                if self.iters == 0:
                    self.iters = data["iters"]
                self.queue.put((device_id, data))
            elif "acc_transtime" in data and "acc_proctime" in data:
                self.transtime += data["acc_transtime"]
                self.logger.info(
                    f"Accumulated transmission time from IoT device {device_id}: {data['acc_transtime']}s"
                )

        pidt: threading.Thread = None
        try:
            self.running.set()

            # Decide the thread target based on job type
            if self.job == "recv":
                pidt = threading.Thread(target=self.process_iot_data, daemon=True)
            elif self.job == "send":
                self.sio_client.connect(
                    self.cloud_addr,
                    headers={"device_id": self.device_id},
                    transports=["websocket"],
                )
                self.logger.info(f"Connected to cloud ({self.cloud_addr})")
                pidt = threading.Thread(target=self.emit_data_to_cloud, daemon=True)
            if pidt:
                pidt.start()
            server_thread.wait()
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
        finally:
            # Ensure the thread is joined and resources are cleaned up
            if pidt and pidt.is_alive():
                pidt.join()
            self.stop()

    def stop(self):
        """
        Stop the edge node gracefully.
        """
        self.logger.info("Stopping edge node...")
        self.running.clear()
        self.sio_client.disconnect()
        self.sio_server.shutdown()
        if self.queue.unfinished_tasks > 0:
            self.queue.join()