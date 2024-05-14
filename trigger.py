import os
from typing import List
from constants import DEFAULT_ITERATIONS
from config import DATA_CONFIG
from helpers.common import get_device_id, get_nid
from dotenv import load_dotenv
from network.IoTClient import IoTClient
from network.EdgeNode import EdgeNode
from network.CloudServer import CloudServer


def start_iot(device_id: str, algo_code: str, iterations: int) -> None:
    try:
        if algo_code not in DATA_CONFIG:
            raise ValueError(f"Invalid algorithm code: {algo_code}")

        algo = DATA_CONFIG.get(algo_code)

        # Get edge node addresses
        NUM_EDGE_NODES = int(os.getenv("NUM_EDGE_NODES"))
        EDGE_NODE_ADDRESSES = [
            os.getenv(f"EDGE_{i+1}_ADDRESS") for i in range(NUM_EDGE_NODES)
        ]

        iot_clients: List[IoTClient] = []
        for i, edge_address in enumerate(EDGE_NODE_ADDRESSES):
            iot_client = IoTClient(
                device_id=f"{device_id}-t{i+1}",
                edge_address=edge_address,
                data_dir=algo["data_dir"],
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
            iot_client.stop()


def start_edge(device_id: str) -> None:
    try:
        edge_node = EdgeNode(device_id)
        edge_node.run()
    except (KeyboardInterrupt, SystemExit, Exception) as e:
        if isinstance(e, Exception):
            edge_node.logger.error(f"An error occurred: {e}")
        edge_node.stop()


def start_cloud(device_id: str) -> None:
    try:
        cloud = CloudServer(device_id)
        cloud.run()
    except (KeyboardInterrupt, SystemExit, Exception) as e:
        if isinstance(e, Exception):
            cloud.logger.error(f"An error occurred: {e}")
        cloud.print_stats()
        cloud.stop()


if __name__ == "__main__":
    load_dotenv()

    # Print available roles with their arguments
    print("=" * 40)
    print("Available roles:")
    print("iot <id> <algo_code> <iterations>")
    print("edge <id>")
    print("cloud <id>")
    print("=" * 40)

    try:
        params = input("Set up device parameters: ").strip().split(" ")
        role = params[0]
        id = params[1]
        device_id = get_nid(role, id)

        if role == "iot":
            algo_code = params[2] if len(params) > 2 else list(DATA_CONFIG.keys())[0]
            iterations = int(params[3]) if len(params) > 3 else DEFAULT_ITERATIONS
            start_iot(device_id, algo_code, iterations)
        elif role == "edge":
            start_edge(device_id)
        elif role == "cloud":
            start_cloud(device_id)

    except Exception as e:
        print("An error occurred:", e)
