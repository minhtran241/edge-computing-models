import os
import sys
from constants import ITERATIONS
from config import DATA_CONFIG
from helpers.common import get_device_id
from dotenv import load_dotenv
from network.IoTClient import IoTClient
from network.EdgeNode import EdgeNode
from network.CloudServer import CloudServer


def start_iot():
    try:
        # Check for command-line argument
        if len(sys.argv) < 4:
            raise ValueError("Usage: python main.py iot <algo_code> <iterations>")
        algo_code = sys.argv[2]
        if algo_code not in DATA_CONFIG:
            raise ValueError(f"Invalid algorithm code: {algo_code}")

        algo = DATA_CONFIG.get(algo_code)
        iterations = int(sys.argv[3]) if len(sys.argv) > 2 else ITERATIONS

        print(f"Running {algo['name']} IoT client with {iterations} iterations...")

        # Get edge node addresses
        NUM_EDGE_NODES = int(os.getenv("NUM_EDGE_NODES"))
        EDGE_NODE_ADDRESSES = [
            os.getenv(f"EDGE_{i+1}_ADDRESS") for i in range(NUM_EDGE_NODES)
        ]

        iot_clients = []
        for i, edge_address in enumerate(EDGE_NODE_ADDRESSES):
            iot_client = IoTClient(
                device_id=f"iot-{i+1}",
                edge_address=edge_address,
                data=algo["data_file"],
                algo=algo_code,
                iterations=iterations,
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


def start_edge():
    device_id = sys.argv[2] if len(sys.argv) > 2 else "edge-1"
    edge_node = EdgeNode(device_id=device_id)

    @edge_node.sio_server.event
    def connect(sid, environ):
        device_id = get_device_id(environ) or sid
        edge_node.sio_server.save_session(sid, {"device_id": device_id})
        edge_node.logger.info(f"IoT device {device_id} connected, session ID: {sid}")

    @edge_node.sio_server.event
    def disconnect(sid):
        session = edge_node.sio_server.get_session(sid)
        device_id = session["device_id"]
        edge_node.logger.info(f"IoT device {device_id} disconnected")

    @edge_node.sio_server.event
    def recv(sid, data):
        session = edge_node.sio_server.get_session(sid)
        device_id = session["device_id"]
        if "data" in data and data["data"] is not None:
            # Print the data received from the IoT device
            edge_node.logger.info(f"Received data from IoT device {device_id}")
            # Sample: data = {"fsize": fsize, "fpath": fpath, "data": formatted, "algo": algo}
            edge_node.queue.put((device_id, data))
        elif "acc_transtime" in data and data["acc_transtime"] is not None:
            edge_node.transtime += data["acc_transtime"]
            edge_node.logger.info(
                f"Accumulated transmission time from IoT device {device_id}: {data['acc_transtime']}s"
            )

    try:
        edge_node.run()
    except (KeyboardInterrupt, SystemExit, Exception) as e:
        if isinstance(e, Exception):
            edge_node.logger.error(f"An error occurred: {e}")
        edge_node.logger.info("Edge node stopped.")
        edge_node.stop()
        sys.exit(0)


def start_cloud():
    try:
        cloud = CloudServer()
        cloud.run()
    except (KeyboardInterrupt, SystemExit, Exception) as e:
        if isinstance(e, Exception):
            cloud.logger.error(f"An error occurred: {e}")
        cloud.print_stats()
        cloud.logger.info("Cloud server stopped.")
        cloud.sio.shutdown()


if __name__ == "__main__":
    load_dotenv()

    if len(sys.argv) < 2:
        raise ValueError("Usage: python main.py <role> optional_args")

    role = sys.argv[1]
    if role == "iot":
        start_iot()
    elif role == "edge":
        start_edge()
    elif role == "cloud":
        start_cloud()
    else:
        raise ValueError(f"Invalid role: {role}")
