import socketio
import time
import threading
from typing import List, Any
from utils.constants import EDGE_NODE_ADDRESSES
from utils.helper_functions import get_img_batches
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

    def __init__(self, device_id: str, edge_address: str, data: Any):
        """
        Initializes the IoTClient object.

        Args:
            device_id (str): The unique identifier of the IoT device.
            edge_address (str): The address of the edge node.
        """
        super().__init__()
        self.device_id = device_id
        self.edge_address = edge_address
        self.data = data
        self.sio = socketio.Client()  # Socket.IO client
        self.logger = Logger(name=f"IoTClient-{device_id}").get_logger()
        self.running = threading.Event()  # Event to control the client's running state
        self.running.set()  # Set the event to True initially

    def send(self):
        """
        Sends data to edge nodes.
        """
        start_transmission = time.time()
        for i, data_batch in enumerate(self.data):
            # Emit data to edge node via Socket.IO
            self.sio.emit("recv", data=data_batch)
            # Log the sent data
            self.logger.info(
                f"Sent batch {i+1}: {len(data_batch)} images to edge node ({self.edge_address})"
            )
        end_transmission = time.time()
        self.logger.info(
            f"Transmission time: {end_transmission - start_transmission:.4f} seconds"
        )

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
    # Split the images into batches for each edge node. Edge node is Raspberry Pi 4 so proper batch size is 3
    data = get_img_batches(
        dir="coco128/images/train2017",
        num_parts=len(EDGE_NODE_ADDRESSES),
        max_batch_size=3,
    )  # [[[img1, img2], [img1, img2]], [[img1, img2], [img1, img2]], [[img1, img2], [img1, img2]]]
    # Create IoTClient instances for each edge node
    iot_clients: List[IoTClient] = []
    for i, edge_address in enumerate(EDGE_NODE_ADDRESSES):
        iot_client = IoTClient(
            device_id=f"iot-{i+1}-{edge_address}",
            edge_address=edge_address,
            data=data[i],
        )
        iot_clients.append(iot_client)
        iot_client.start()

    # # Simulate running for a while
    # time.sleep(30)

    # # Stop all IoT clients
    # for iot_client in iot_clients:
    #     iot_client.stop_client()

    # # Wait for all IoT clients to finish
    for iot_client in iot_clients:
        iot_client.join()

    # Wait for About 100s
    time.sleep(100)
    # print("All IoT clients finished.")
