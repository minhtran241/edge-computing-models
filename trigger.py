import os
from typing import List
from constants import DEFAULT_ITERATIONS, DEFAULT_DATA_SIZE_OPTION
from helpers.common import get_nid, safe_int
from models.enums import Algorithm, ModelArch
from dotenv import load_dotenv
from network.IoTClient import IoTClient
from network.EdgeNode import EdgeNode
from network.CloudServer import CloudServer


def start_iot(
    device_id: str, algo_code: str, size_option: str, iterations: int, arch_name: str
) -> None:
    iot_clients: List[IoTClient] = (
        []
    )  # Initialize the iot_clients list outside the try block
    try:
        algo = Algorithm[algo_code]
        # Check if the algorithm and size option are supported
        if size_option not in algo.value["avail_sizes"]:
            raise ValueError(
                f"Invalid data size option: {size_option}. Supported options: {algo.value['avail_sizes']}"
            )
        arch = ModelArch[arch_name]

        # Get edge node addresses
        NUM_TARGET_NODES = int(os.getenv("NUM_IOT_TARGETS"))
        TARGET_NODE_ADDRESSES = [
            os.getenv(f"IOT_TARGET_{i+1}") for i in range(NUM_TARGET_NODES)
        ]

        for i, ta in enumerate(TARGET_NODE_ADDRESSES):
            iot_client = IoTClient(
                device_id=f"{device_id}-t{i+1}",
                target_address=ta,
                size_option=size_option,
                algo=algo,
                iterations=iterations,
                arch=arch,
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


def start_cloud(device_id: str, arch_name: str) -> None:
    try:
        arch: ModelArch = ModelArch[arch_name]
        cloud = CloudServer(device_id, arch=arch)
        cloud.run()
    except (KeyboardInterrupt, SystemExit, Exception) as e:
        if isinstance(e, Exception):
            cloud.logger.error(f"An error occurred: {e}")
        if len(cloud.data) > 0:
            cloud.print_stats()
        cloud.stop()


if __name__ == "__main__":
    load_dotenv()

    # Print available roles with their arguments
    print("=" * 40)
    print("Available roles:")
    print("iot <id> <algo_code> <size_option> <iterations>")
    print("edge <id>")
    print("cloud <id>")
    print("=" * 40)

    try:
        params = input("Set up device parameters: ").strip().split(" ")
        role = params[0]
        id = params[1]
        device_id = get_nid(role, id)

        arch_name: str = input(
            f"Set up model architecture {ModelArch._member_names_}: "
        ).upper()

        if role == "iot":
            algo_code = params[2].upper() if len(params) > 2 else "SW"
            size_option = params[3] if len(params) > 3 else DEFAULT_DATA_SIZE_OPTION
            iterations = (
                safe_int(params[4], DEFAULT_ITERATIONS)
                if len(params) > 4
                else DEFAULT_ITERATIONS
            )

            start_iot(
                device_id=device_id,
                algo_code=algo_code,
                size_option=size_option,
                iterations=iterations,
                arch_name=arch_name,
            )
        elif role == "edge":
            start_edge(device_id)
        elif role == "cloud":
            start_cloud(device_id, arch_name)
        else:
            print(f"Unknown role: {role}")

    except Exception as e:
        print("An error occurred:", e)
