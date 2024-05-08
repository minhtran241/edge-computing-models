import eventlet
import socketio
import pandas as pd
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
        self.transtimes = {}
        self.proctimes = {}
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

    # Print stats of specific edge node
    def _print_statistics(self, device_id: str):
        """
        Print the statistics for each edge node upon disconnection.
        """
        df = pd.DataFrame(
            {
                "Device ID": [device_id],
                "Total Transmission Time": [self.transtimes.get(device_id, 0)],
                "Total Processing Time": [self.proctimes.get(device_id, 0)],
            }
        )
        print(df.to_markdown())
        self.logger.info(f"Edge node {device_id} disconnected")

    # Print all stats of all edge nodes
    def print_statistics(self):
        """
        Print the statistics for all edge nodes.
        """
        df = pd.DataFrame(
            {
                "Device ID": list(self.transtimes.keys()),
                "Total Transmission Time": list(self.transtimes.values()),
                "Total Processing Time": list(self.proctimes.values()),
            }
        )
        print(df.to_markdown())

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
            self.logger.info(f"Edge node {device_id} connected, session ID: {sid}")

        @self.sio.event
        def disconnect(sid):
            session = self.sio.get_session(sid)
            device_id = session["device_id"]
            self._print_statistics(device_id)

        @self.sio.event
        def recv(sid, data):
            session = self.sio.get_session(sid)
            device_id = session["device_id"]
            if "transtime" in data or "proctime" in data:
                self.transtimes[device_id] = data.get("transtime", 0)
                self.proctimes[device_id] = data.get("proctime", 0)
                return
            self.process_edge_data(device_id, data["data"])

        server_thread.wait()


if __name__ == "__main__":
    try:
        cloud = CloudServer()
        cloud.run()
    except KeyboardInterrupt or SystemExit or Exception as e:
        if isinstance(e, Exception):
            cloud.logger.error(f"An error occurred: {e}")
        cloud.print_statistics()
        cloud.logger.info("Cloud server stopped.")
        cloud.sio.shutdown()
        exit()
