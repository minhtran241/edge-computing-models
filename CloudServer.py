import eventlet
import socketio
import time
from typing import Any
from Logger import Logger
from utils.helper_functions import get_device_id


class CloudServer:
    """
    Cloud server class to receive processed data from edge nodes.
    """

    def __init__(self, port: int = 20000):
        """
        Initialize the CloudServer instance.

        Args:
            port (int, optional): The port on which the cloud server will run. Defaults to 20000.
        """
        self.port = port
        self.sio = socketio.Server()
        self.app = socketio.WSGIApp(self.sio)
        self.logger = Logger(name="CloudServer").get_logger()
        self.transmission_times = {}
        self.processing_times = {}
        self.result = 0

    def process_edge_data(self, device_id: str, data: Any):
        """
        Receive data from an edge node.

        Args:
            device_id (str): The identifier of the edge node.
            data int: The processed data received from the edge node.
        """
        self.logger.info(
            f"Received data from edge node {device_id}: {len(data)} image results"
        )
        self.result += len(data)
        self.logger.info(f"Total results: {self.result}")

    def run_server(self):
        """
        Run the cloud server.
        """
        try:
            eventlet.wsgi.server(
                eventlet.listen(("", self.port)),
                self.app,
            )
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")

    def run(self):
        """
        Start the cloud server and set up event handlers.
        """
        server_thread = eventlet.spawn(self.run_server)

        @self.sio.event
        def connect(sid, environ):
            device_id = get_device_id(environ) or sid
            self.sio.save_session(sid, {"device_id": device_id})
            self.logger.info(f"Edge node {sid} connected")

        @self.sio.event
        def disconnect(sid):
            session = self.sio.get_session(sid)
            device_id = session["device_id"]
            # Print the statistics for the edge node upon disconnection as a table with the following columns: Device ID, Total Transmission Time, Total Processing Time
            self.logger.info(
                f"Edge node {device_id} disconnected\n"
                f"{'Device ID':<15}{'Total Transmission Time':<25}{'Total Processing Time':<25}"
            )

        @self.sio.event
        def recv(sid, data):
            session = self.sio.get_session(sid)
            device_id = session["device_id"]
            transmission_time = (
                time.time()
                - data.get("start_transmission", 0)
                + data.get("prev_ttime", 0)
            )
            self.transmission_times.setdefault(device_id, 0)
            self.transmission_times[device_id] += transmission_time
            self.processing_times.setdefault(device_id, 0)
            self.processing_times[device_id] += data.get("prev_ptime", 0)
            self.process_edge_data(device_id, data["data"])

        server_thread.wait()


if __name__ == "__main__":
    cloud = CloudServer()
    cloud.run()
