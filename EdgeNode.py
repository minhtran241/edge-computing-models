import sys
import threading
import eventlet
import socketio
import time
import queue
from typing import Any
from ultralytics import YOLO
from Logger import Logger
from utils.constants import CLOUD_ADDRESS
from utils.helper_functions import get_device_id, ocr_license_plate


class EdgeNode:
    def __init__(
        self,
        device_id: str,
        port: int = 10000,
        cloud_addr: str = CLOUD_ADDRESS,
    ):
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
        while self.running.is_set():
            try:
                device_id, data = self.queue.get(timeout=1)
                self._process_iot_data(device_id, data)
            except queue.Empty:
                pass

    def _process_iot_data(self, device_id: str, data: Any):
        start_time = time.time()
        data = ocr_license_plate(data)
        self.proctime += time.time() - start_time
        start_time = time.time()
        self.sio_client.emit(
            "recv",
            data={"data": data},
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
        if "acc_transtime" in data and data["acc_transtime"] is not None:
            edge_node.transtime += data["acc_transtime"]
            edge_node.logger.info(
                f"Accumulated transmission time from IoT device {device_id}: {data['acc_transtime']}s"
            )
        elif "data" in data and data["data"] is not None:
            edge_node.logger.info(
                f"Received data from IoT device {device_id}: {data['fsize']} bytes"
            )
            edge_node.queue.put((device_id, data["data"]))

    try:
        edge_node.run()
    except (KeyboardInterrupt, SystemExit, Exception) as e:
        if isinstance(e, Exception):
            edge_node.logger.error(f"An error occurred: {e}")
        edge_node.logger.info("Edge node stopped.")
        edge_node.stop()
        sys.exit(0)
