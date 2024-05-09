import sys
import threading
import eventlet
import socketio
import time
import queue
from typing import Any
from ultralytics import YOLO
from Logger import Logger
from constants import CLOUD_ADDRESS
from helpers.common import get_device_id
from helpers.ocr import ocr_license_plate


class EdgeNode:
    """
    Edge node class to process data from IoT devices and send it to the cloud.
    """

    def __init__(
        self,
        device_id: str,
        port: int = 10000,
        cloud_addr: str = CLOUD_ADDRESS,
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
        self.model = YOLO("yolov8m.pt")
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
            except queue.Empty:
                pass

    def _process_iot_data(self, device_id: str, data: Any):
        """
        Process the data received from an IoT device.

        Args:
                        device_id (str): The identifier of the IoT device.
                        data (Any): The data received from the IoT device.
        """
        # Sample: data = {"fsize": fsize, "img_path": img_path, "data": img_data}
        fsize = data["fsize"]
        img_path = data["img_path"]
        img_data = data["data"]
        start_time = time.time()
        result = ocr_license_plate(img_data)
        self.proctime += time.time() - start_time
        sent_data = {"fsize": fsize, "img_path": img_path, "data": result}
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


if __name__ == "__main__":
    device_id = sys.argv[1] if len(sys.argv) > 1 else "edge-1"
    edge_node = EdgeNode(device_id=device_id)

    @edge_node.sio_server.event
    def connect(sid, environ):
        device_id = get_device_id(environ) or sid
        edge_node.sio_server.save_session(sid, {"device_id": device_id})
        edge_node.logger.info(f"IoT device {device_id} connected, session ID: {sid}")

    @edge_node.sio_server.event
    def disconnect(sid):
        session = edge_node.sio_server.get_session(sid)
        device_id = session["device_id"]
        edge_node.logger.info(f"IoT device {device_id} disconnected")

    @edge_node.sio_server.event
    def recv(sid, data):
        session = edge_node.sio_server.get_session(sid)
        device_id = session["device_id"]
        if "data" in data and data["data"] is not None:
            # Print the data received from the IoT device
            edge_node.logger.info(f"Received data from IoT device {device_id}")
            # Sample: data["data"] = {"fsize": fsize, "img_path": img_path, "data": img_data}
            edge_node.queue.put((device_id, data))
        elif "acc_transtime" in data and data["acc_transtime"] is not None:
            edge_node.transtime += data["acc_transtime"]
            edge_node.logger.info(
                f"Accumulated transmission time from IoT device {device_id}: {data['acc_transtime']}s"
            )

    try:
        edge_node.run()
    except (KeyboardInterrupt, SystemExit, Exception) as e:
        if isinstance(e, Exception):
            edge_node.logger.error(f"An error occurred: {e}")
        edge_node.logger.info("Edge node stopped.")
        edge_node.stop()
        sys.exit(0)
