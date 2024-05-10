import sys
import os
import socketio
import time
import threading
from typing import Any
from constants import ITERATIONS
from config import DATA_CONFIG
from Logger import Logger
from dotenv import load_dotenv

load_dotenv()


class IoTClient(threading.Thread):
    """
    IoT client class to send data to edge nodes.
    """

    def __init__(self, device_id: str, edge_address: str, data: Any, algo: str):
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
        self.algo = algo
        self.sio = socketio.Client()  # Socket.IO client
        self.transtime = (
            0  # Transmission time from IoT device to edge node (accumulated)
        )
        self.logger = Logger(name=f"IoTClient-{device_id}").get_logger()
        self.running = threading.Event()  # Event to control the client's running state
        self.running.set()  # Set the event to True initially
        self.lock = threading.Lock()  # Lock to ensure thread safety

    def send(self):
        """
        Sends data to edge nodes.
        """
        for _ in range(ITERATIONS):
            fsize = os.path.getsize(self.data)

            formatted = DATA_CONFIG[self.algo]["preprocess"](self.data)

            sent_data = {
                "fsize": fsize,
                "fpath": self.data,
                "algo": self.algo,
                "data": formatted,
            }

            with self.lock:
                start_time = time.time()
                self.sio.emit("recv", data=sent_data)
                self.transtime += time.time() - start_time

        with self.lock:
            self.sio.emit("recv", data={"acc_transtime": self.transtime})

    def run(self):
        """
        Runs the IoT client.
        """
        try:
            self.sio.connect(self.edge_address, headers={"device_id": self.device_id})
            self.logger.info(f"Connected to edge node ({self.edge_address})")
            self.send()
            self.sio.wait()
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")

    def stop_client(self):
        """
        Stops the IoT client gracefully.
        """
        self.running.clear()
        self.disconnect_from_edge()
        self.logger.info("IoT client stopped.")

    def disconnect_from_edge(self):
        """
        Disconnects from the edge node.
        """
        self.sio.disconnect()
        self.logger.info(f"Disconnected from edge node ({self.edge_address}).")

    def __del__(self):
        self.stop_client()


if __name__ == "__main__":
    try:
        # Check for command-line argument
        if len(sys.argv) < 2:
            raise ValueError("Usage: python IoTClient.py <algorithm>")

        algo_code = sys.argv[1]
        algo = DATA_CONFIG.get(algo_code)
        if not algo:
            raise ValueError(f"Invalid algorithm: {algo_code}")

        print(f"Running {algo['name']} IoT client...")

        # Get edge node addresses
        NUM_EDGE_NODES = int(os.getenv("NUM_EDGE_NODES"))
        EDGE_NODE_ADDRESSES = [
            os.getenv(f"EDGE_{i+1}_ADDRESS") for i in range(NUM_EDGE_NODES)
        ]

        # Get data file path and send the same data to all edge nodes
        data_file = algo["data_file"]
        print(f"Sending data from {data_file} to edge nodes...")

        iot_clients = []
        for i, edge_address in enumerate(EDGE_NODE_ADDRESSES):
            iot_client = IoTClient(
                device_id=f"iot-{i+1}",
                edge_address=edge_address,
                data=data_file,
                algo=algo_code,
            )
            iot_clients.append(iot_client)
            iot_client.start()

        for iot_client in iot_clients:
            iot_client.join()

    except (ValueError, KeyboardInterrupt, SystemExit) as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        for iot_client in iot_clients:
            iot_client.stop_client()
        print("IoT clients stopped.")
