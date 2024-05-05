import socketio
import random
import time
import threading
from typing import List
from utils.constants import EDGE_NODE_ADDRESSES
from Logger import Logger


class IoTClient(threading.Thread):
    """
    Class representing an IoT client that sends data to edge nodes.

    Attributes:
        device_id (str): The unique identifier of the IoT device.
        edge_address (str): Address of the edge node.
        sio (socketio.Client): Socket.IO client instance.
        logger (Logger): Logger instance for logging.

    Methods:
        __init__: Initializes the IoTClient object.
        send: Sends data to edge nodes.
        run: Runs the IoT client.
        stop_client: Stops the IoT client gracefully.
        disconnect_from_edge: Disconnects from the edge node.
    """

    def __init__(self, device_id: str, edge_address: str):
        """
        Initializes the IoTClient object.

        Args:
            device_id (str): The unique identifier of the IoT device.
            edge_address (str): The address of the edge node.
        """
        super().__init__()
        self.device_id = device_id
        self.edge_address = edge_address
        self.sio = socketio.Client()  # Socket.IO client
        self.logger = Logger(name=f"IoTClient-{device_id}").get_logger()
        self.running = threading.Event()  # Event to control the client's running state

    def send(self):
        """
        Sends data to edge nodes.
        """
        while self.running.is_set():
            # Generate random temperature and humidity data
            data = {
                "temperature": random.randint(20, 30),
                "humidity": random.randint(60, 80),
            }
            # Emit data to edge node via Socket.IO
            self.sio.emit("recv", data)
            # Log the sent data
            self.logger.info(f"Sent data to edge node: {data}")
            # Wait for 5 seconds before sending the next data
            time.sleep(5)

    def run(self):
        """
        Runs the IoT client.
        """
        try:
            # Connect to edge node with device ID as header
            self.sio.connect(self.edge_address, headers={"device_id": self.device_id})
            # Log successful connection to edge node
            self.logger.info(f"Connected to edge node ({self.edge_address})")
            # Start sending data to edge nodes
            self.send()
        except Exception as e:
            # Log any errors that occur during execution
            self.logger.error(f"An error occurred: {e}")

    def stop_client(self):
        """
        Stops the IoT client gracefully.
        """
        self.running.clear()  # Clear the running event
        self.disconnect_from_edge()  # Disconnect from the edge node
        self.logger.info("IoT client stopped.")

    def disconnect_from_edge(self):
        """
        Disconnects from the edge node.
        """
        self.sio.disconnect()
        self.logger.info(f"Disconnected from edge node ({self.edge_address}).")


# Entry point for the script
if __name__ == "__main__":
    # Create IoTClient instances for each edge node
    iot_clients: List[IoTClient] = []
    for i, edge_address in enumerate(EDGE_NODE_ADDRESSES):
        iot_client = IoTClient(
            device_id=f"iot-{i+1}-{edge_address}", edge_address=edge_address
        )
        iot_clients.append(iot_client)
        iot_client.start()

    # Simulate running for a while
    time.sleep(30)

    # Stop all IoT clients
    for iot_client in iot_clients:
        iot_client.stop_client()
