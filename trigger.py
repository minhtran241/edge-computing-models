import os
import sys
from constants import ITERATIONS
from config import DATA_CONFIG
from helpers.common import get_device_id, get_nid
from dotenv import load_dotenv
from network.IoTClient import IoTClient
from network.EdgeNode import EdgeNode
from network.CloudServer import CloudServer


def start_iot(device_id: str, algo_code: str, iterations: int):
    try:
        if algo_code not in DATA_CONFIG:
            raise ValueError(f"Invalid algorithm code: {algo_code}")

        algo = DATA_CONFIG.get(algo_code)

        # Get edge node addresses
        NUM_EDGE_NODES = int(os.getenv("NUM_EDGE_NODES"))
        EDGE_NODE_ADDRESSES = [
            os.getenv(f"EDGE_{i+1}_ADDRESS") for i in range(NUM_EDGE_NODES)
        ]

        iot_clients = []
        for i, edge_address in enumerate(EDGE_NODE_ADDRESSES):
            iot_client = IoTClient(
                device_id=f"{device_id}-t{i+1}",
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


def start_edge(device_id: str):
    edge_node = EdgeNode(device_id)

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


def start_cloud(device_id: str):
    try:
        cloud = CloudServer(device_id)
        cloud.run()
    except (KeyboardInterrupt, SystemExit, Exception) as e:
        if isinstance(e, Exception):
            cloud.logger.error(f"An error occurred: {e}")
        cloud.print_stats()
        cloud.logger.info("Cloud server stopped.")
        cloud.sio.shutdown()


if __name__ == "__main__":
    load_dotenv()

    # Print available roles with there arguments
    print("================")
    print("Available roles:")
    print("iot <id> <algo_code> <iterations>")
    print("edge <id>")
    print("cloud <id>")
    print("================")
    try:
        params = input("Set up device parameters: ").strip().split(" ")
        role = params[0]
        id = params[1]
        device_id = get_nid(role, id)
        if role == "iot":
            algo_code = params[2] if len(params) > 2 else DATA_CONFIG.keys()[0]
            iterations = int(params[3]) if len(params) > 3 else ITERATIONS
            start_iot(device_id, algo_code, iterations)
        elif role == "edge":
            start_edge(device_id)
        elif role == "cloud":
            start_cloud(device_id)
    except:
        print("Invalid arguments.")
        sys.exit(1)
