import eventlet
import socketio
import queue
import threading
from dotenv import load_dotenv
import pandas as pd
from tabulate import tabulate
from helpers.common import get_device_id, process_data, print_dict
from helpers.logger import Logger
from models.enums import ModelArch, Algorithm

load_dotenv()


class CloudServer:
    """
    Cloud server class to receive and process data from client nodes.

    :param device_id: The unique identifier of the cloud server.
    :type device_id: str
    :param port: The port on which the cloud server will run, defaults to 20000.
    :type port: int, optional
    :param arch: The architecture type, either 'Edge' or 'Cloud', defaults to ModelArch.EDGE.
    :type arch: ModelArch, optional
    """

    def __init__(self, device_id: str, arch: ModelArch, port: int = 20000):
        self.device_id = device_id
        self.port = port
        self.arch = arch
        self.sio = socketio.Server(
            always_connect=True,
            max_http_buffer_size=10**8,
            engineio_logger=True,
            ping_interval=10
            ** 8,  # Set ping interval to infinity to prevent disconnections
            http_compression=False,
        )
        self.app = socketio.WSGIApp(self.sio)
        self.logger = Logger(self.device_id)
        self.queue = queue.Queue()
        self.data = {}
        self.num_recv_packets = 0
        self.num_proc_packets = 0
        self.transtimes = {}
        self.proctimes = {}

        # Log the initialization details
        self.logger.info(
            {"device_id": self.device_id, "port": self.port, "arch": self.arch.name}
        )

    def process_recv_data(self):
        """
        Process the received data from IoT devices.
        This function runs in a separate thread to continuously process data from the queue.
        """
        while True:
            try:
                device_id, data = self.queue.get(
                    timeout=1
                )  # Fetch data from the queue with timeout
                algo = Algorithm[data["algo"]]  # Get the algorithm type
                recv_data = data["data"]  # Extract the received data

                # Process the data using the algorithm's processing function
                result, pt = process_data(func=algo.value["process"], data=recv_data)

                # Update the processed data count and log the result
                self.num_proc_packets += 1
                self.logger.info(
                    f"(#{self.num_proc_packets}) Processed data from node {device_id}: {result}"
                )

                # Update processing times and store the result
                with threading.Lock():
                    self.proctimes[device_id] += pt
                    self.data.setdefault(device_id, []).append(
                        {
                            "arch": data["arch"],
                            "data_size": data["data_size"],
                            "data_dir": data["data_dir"],
                            "algo": data["algo"],
                            "data": result,
                            "iot_device_id": device_id,
                        }
                    )
                self.queue.task_done()  # Mark the task as done in the queue
            except queue.Empty:
                continue  # Continue if the queue is empty

    def print_stats(self):
        """
        Print the statistics for all client nodes.
        This function calculates and displays the number of files received, total file size,
        and average transmission and processing times.
        """
        arch = self.arch
        num_files = sum(len(files) for files in self.data.values())
        total_size = sum(d["data_size"] for files in self.data.values() for d in files)

        # Calculate average transmission and processing times
        transtime = sum(self.transtimes.values()) / len(self.transtimes)
        proctime = sum(self.proctimes.values()) / len(self.proctimes)

        if arch == ModelArch.EDGE:
            df = pd.DataFrame(
                {
                    "Device ID": list(self.transtimes.keys()),
                    "Files Received": [len(files) for files in self.data.values()],
                    "Total File Size": [
                        sum(d["data_size"] for d in files)
                        for files in self.data.values()
                    ],
                    "Transmission Time": list(self.transtimes.values()),
                    "Processing Time": list(self.proctimes.values()),
                }
            )
            print(tabulate(df, headers="keys", tablefmt="pretty", showindex=False))

        # Print overall statistics
        print_dict(
            {
                "Architecture": arch.name,
                "Number of Files Received": num_files,
                "Total File Size": total_size,
                "Receive From": list(self.transtimes.keys()),
                "Transmission Time": transtime,
                "Processing Time": proctime,
            }
        )

    def run_server(self):
        """
        Run the cloud server using eventlet's WSGI server.
        This function handles incoming connections and serves the application.
        """
        try:
            eventlet.wsgi.server(eventlet.listen(("", self.port)), self.app)
        except Exception as e:
            self.logger.error(f"An error occurred while running the server: {e}")

    def run(self):
        """
        Start the cloud server, set up event handlers, and handle incoming data.
        This function spawns a server thread and sets up event handlers for client connections, disconnections,
        and data reception.
        """
        server_thread = eventlet.spawn(self.run_server)

        @self.sio.event
        def connect(sid, environ):
            device_id = (
                get_device_id(environ) or sid
            )  # Retrieve or generate a device ID
            self.sio.save_session(sid, {"device_id": device_id})
            self.logger.info(f"Client node {device_id} connected, session ID: {sid}")

        @self.sio.event
        def disconnect(sid):
            session = self.sio.get_session(sid)
            device_id = session["device_id"]
            self.logger.info(f"Client node {device_id} disconnected")

        @self.sio.event
        def recv(sid, data):
            session = self.sio.get_session(sid)
            device_id = session["device_id"]

            # Initialize data structures if not already present
            self.data.setdefault(device_id, [])
            self.transtimes.setdefault(device_id, 0)
            self.proctimes.setdefault(device_id, 0)

            if "data" in data and data["data"] is not None:
                self.num_recv_packets += 1
                if self.arch == ModelArch.CLOUD:
                    self.queue.put((device_id, data))  # Queue the data for processing
                else:
                    self.logger.info(
                        f"(#{self.num_recv_packets}) Result from client node {device_id}: {data}"
                    )
                    self.data[device_id].append(data)
            elif "acc_transtime" in data and "acc_proctime" in data:
                self.logger.info(
                    {
                        "device_id": device_id,
                        "acc_transtime": data["acc_transtime"],
                        "acc_proctime": data["acc_proctime"],
                    }
                )
                self.transtimes[device_id] += data["acc_transtime"]
                self.proctimes[device_id] += data["acc_proctime"]

        if self.arch == ModelArch.CLOUD:
            threading.Thread(target=self.process_recv_data, daemon=True).start()

        server_thread.wait()

    def stop(self):
        """
        Stop the cloud server gracefully.
        """
        self.logger.info("Stopping cloud server...")
        self.sio.shutdown()
