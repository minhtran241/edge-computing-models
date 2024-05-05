import eventlet
import socketio
from typing import Dict
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

    def process_edge_data(self, device_id: str, data: Dict[str, int]):
        """
        Receive data from an edge node.

        Args:
            device_id (str): The identifier of the edge node.
            data (Dict[str, int]): The processed data received from the edge node.
        """
        self.logger.info(f"Received data from edge node {device_id}: {data}")

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
            self.logger.info(f"Edge node {sid} disconnected")

        @self.sio.event
        def receive_data(sid, data):
            session = self.sio.get_session(sid)
            self.process_edge_data(session["device_id"], data)

        server_thread.wait()


if __name__ == "__main__":
    cloud = CloudServer()
    cloud.run()
