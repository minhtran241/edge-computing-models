import os
import threading
import eventlet
import socketio
import queue
from typing import Any
from dotenv import load_dotenv
from helpers.logger import Logger
from helpers.common import get_device_id, process_data, emit_data
from helpers.models import Algorithm

load_dotenv()


class EdgeNode:
    """
    Edge node class to process data from IoT devices and send it to the cloud.
    """

    def __init__(
        self,
        device_id: str,
        port: int = 10000,
        cloud_addr: str = os.getenv("EDGE_TARGET"),
    ):
        """
        Initialize the EdgeNode instance.

        Args:
            device_id (str): The unique identifier of the edge node.
            port (int, optional): The port on which the edge node will run. Defaults to 10000.
            cloud_addr (str, optional): The address of the cloud server. Defaults to EDGE_TARGET.
        """
        self.device_id = device_id
        self.cloud_addr = cloud_addr
        self.port = port
        self.sio_client = socketio.Client()
        self.sio_server = socketio.Server(always_connect=True, logger=True)
        self.app = socketio.WSGIApp(self.sio_server)
        self.logger = Logger(self.device_id)
        self.queue = queue.Queue()
        self.transtime = 0
        self.proctime = 0
        self.running = threading.Event()
        self.logger.info(
            {
                "device_id": self.device_id,
                "port": self.port,
                "cloud_addr": self.cloud_addr,
            }
        )

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
        # Sample: data = {"data_size": data_size, "data_dir": data_dir, "data": formatted, "algo": algo}
        recv_data = data["data"]
        algo: Algorithm = Algorithm[data["algo"].upper()]

        result, pt = process_data(func=algo["process"], data=recv_data)
        self.proctime += pt

        # Remain attributes the same, just change the data to the result and the device_id of the IoT device
        sent_data = {
            "arch": data["arch"],
            "data_size": data["data_size"],
            "data_dir": data["data_dir"],
            "algo": algo["name"],
            "data": result,
            "iot_device_id": device_id,
        }

        tt = emit_data(self.sio_client, sent_data)
        self.transtime += tt

        self.sio_client.emit(
            "recv",
            data={
                "acc_transtime": self.transtime,
                "acc_proctime": self.proctime,
            },
        )

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
            # device_id = "iot-1"
            if "data" in data and data["data"] is not None:
                # Sample: data = {"data_size": data_size, "data_dir": data_dir, "data": formatted, "algo": algo}
                self.queue.put((device_id, data))
            elif "acc_transtime" in data and "acc_proctime" in data:
                self.transtime += data["acc_transtime"]
                self.logger.info(
                    f"Accumulated transmission time from IoT device {device_id}: {data['acc_transtime']}s"
                )
                # self.proctime += data["acc_proctime"]
                # self.logger.info(
                #     f"Accumulated processing time from IoT device {device_id}: {data['acc_proctime']}s"
                # )

        try:
            self.running.set()
            pidt = threading.Thread(target=self.process_iot_data, daemon=True)
            pidt.start()
            self.sio_client.connect(
                self.cloud_addr,
                headers={"device_id": self.device_id},
                transports=["websocket"],
            )
            self.logger.info(f"Connected to cloud ({self.cloud_addr})")
            server_thread.wait()
        except Exception as e:
            pidt.join()
            self.logger.error(f"An error occurred: {e}")

    def stop(self):
        """
        Stop the edge node gracefully.
        """
        self.logger.info("Stopping edge node...")
        self.running.clear()
        self.sio_client.disconnect()
        self.sio_server.shutdown()
        # If there are still items in the queue, wait for them to be processed
        if self.queue.unfinished_tasks > 0:
            self.queue.join()
