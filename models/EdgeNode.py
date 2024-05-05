import eventlet
import socketio
from typing import Dict
from models.Logger import Logger
from constants import CLOUD_ADDRESS


class EdgeNode:
    """
    Represents an edge node that receives data from IoT devices, processes it, and sends it to the cloud.
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

    def receive_data_from_iot_device(self, sid: str, data: Dict[str, int]):
        """
        Receive data from an IoT device, process it, and send it to the cloud.

        Args:
            sid (str): The session ID of the IoT device.
            data (Dict[str, int]): The data received from the IoT device.
        """
        self.logger.info(f"Received data from IoT device {sid}: {data}")
        # Process the data
        data["temperature"] += 1
        data["humidity"] += 1
        # Send the processed data to the cloud
        self.sio_client.emit("receive_data_from_edge_node", data)

    def run(self):
        """
        Run the edge node.
        """
        try:
            # Connect to the cloud
            self.sio_client.connect(
                self.cloud_addr, headers={"device_id": self.device_id}
            )
            self.logger.info(f"Connected to cloud ({self.cloud_addr})")
            # Send initial data to the cloud
            self.sio_client.emit(
                "receive_data_from_edge_node", {"temperature": 0, "humidity": 0}
            )
            # Start serving the WSGI app
            eventlet.wsgi.server(eventlet.listen(("", self.port)), self.app)
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")

    @classmethod
    def register_event_handlers(cls, sio_server, logger):
        """
        Register event handlers for Socket.IO server.

        Args:
            sio_server: The Socket.IO server instance.
            logger: The logger instance for logging events.
        """

        @sio_server.event
        def connect(sid, environ):
            logger.info(f"IoT device {sid} connected")

        @sio_server.event
        def disconnect(sid):
            logger.info(f"IoT device {sid} disconnected")

        @sio_server.event
        def receive_data_from_iot_device(sid, data):
            cls.receive_data_from_iot_device(sid, data)


if __name__ == "__main__":
    edge_node = EdgeNode(device_id="edge_1")

    # Register event handlers
    EdgeNode.register_event_handlers(edge_node.sio_server, edge_node.logger)

    # Run the edge node
    edge_node.run()
