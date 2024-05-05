import eventlet
import socketio
from typing import Dict
from Logger import Logger
from utils.constants import CLOUD_ADDRESS
from utils.helper_functions import get_device_id


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

    def process_iot_data(self, device_id: str, data: Dict[str, int]):
        """
        Receive data from an IoT device, process it, and send it to the cloud.

        Args:
            device_id (str): The identifier of the IoT device.
            data (Dict[str, int]): The data received from the IoT device.
        """
        self.logger.info(f"Received data from IoT device {device_id}: {data}")
        # Process the data
        data["temperature"] += 1
        data["humidity"] += 1
        # Send the processed data to the cloud
        self.sio_client.emit("recv", data)

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
            # Start serving the WSGI app
            eventlet.wsgi.server(eventlet.listen(("", self.port)), self.app)
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    edge_node = EdgeNode(device_id="edge-1")

    @edge_node.sio_server.event
    def connect(sid, environ):
        device_id = get_device_id(environ) or sid
        edge_node.sio_server.save_session(sid, {"device_id": device_id})
        edge_node.logger.info(f"IoT device {sid} connected")

    @edge_node.sio_server.event
    def disconnect(sid):
        edge_node.logger.info(f"IoT device {sid} disconnected")

    @edge_node.sio_server.event
    def recv(sid, data):
        session = edge_node.sio_server.get_session(sid)
        edge_node.process_iot_data(session["device_id"], data)

    # Run the edge node
    edge_node.run()
