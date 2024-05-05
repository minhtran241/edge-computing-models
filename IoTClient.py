import socketio
import random
import time
from typing import List
from utils.constants import EDGE_NODE_ADDRESSES
from Logger import Logger


class IoTClient:
    """
    Class representing an IoT client that sends data to edge nodes.

    Attributes:
        device_id (str): The unique identifier of the IoT device.
        edge_node_addrs (List[str]): List of addresses of edge nodes.
        sio (socketio.Client): Socket.IO client instance.
        logger (Logger): Logger instance for logging.

    Methods:
        __init__: Initializes the IoTClient object.
        send_data_to_edge_node: Sends data to edge nodes.
        run: Runs the IoT client.
    """

    def __init__(
        self, device_id: str, edge_node_addrs: List[str] = EDGE_NODE_ADDRESSES
    ):
        """
        Initializes the IoTClient object.

        Args:
            device_id (str): The unique identifier of the IoT device.
            edge_node_addrs (List[str], optional): List of addresses of edge nodes. Defaults to EDGE_NODE_ADDRESSES.
        """
        self.device_id = device_id
        self.edge_node_addrs = edge_node_addrs
        self.sio = socketio.Client()  # Socket.IO client
        self.logger = Logger(name=f"IoTClient-{device_id}").get_logger()

    def send_data_to_edge_node(self):
        """
        Sends data to edge nodes.
        """
        while True:
            # Generate random temperature and humidity data
            data = {
                "temperature": random.randint(20, 30),
                "humidity": random.randint(60, 80),
            }
            # Emit data to edge node via Socket.IO
            self.sio.emit("receive_data", data)
            # Log the sent data
            self.logger.info(f"Sent data to edge node: {data}")
            # Wait for 5 seconds before sending the next data
            time.sleep(5)

    def run(self):
        """
        Runs the IoT client.
        """
        try:
            # Connect to each edge node
            for ena in self.edge_node_addrs:
                # Connect to edge node with device ID as header
                self.sio.connect(ena, headers={"device_id": self.device_id})
                # Log successful connection to edge node
                self.logger.info(f"Connected to edge node ({ena})")
            # Start sending data to edge nodes
            self.send_data_to_edge_node()
        except Exception as e:
            # Log any errors that occur during execution
            self.logger.error(f"An error occurred: {e}")


# Entry point for the script
if __name__ == "__main__":
    # Create an instance of IoTClient with device ID "iot_device_1"
    iot_client = IoTClient(device_id="iot-1")
    # Run the IoT client
    iot_client.run()
