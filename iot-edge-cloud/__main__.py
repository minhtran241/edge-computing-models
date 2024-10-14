import os
import click
from typing import List
from dotenv import load_dotenv
from helpers.common import get_nid
from services import Algorithm, ModelArch
from services.IoTClient import IoTClient
from services.EdgeNode import EdgeNode
from services.CloudServer import CloudServer

load_dotenv()

# Constants
VALID_ROLES: List[str] = ["IOT", "EDGE", "CLOUD"]
DEFAULT_ITERATIONS: int = 54
DEFAULT_DATA_SIZE_OPTION: str = "small"
ROLE = os.environ.get("ROLE", "EDGE").upper()
DEVICE_ID = os.environ.get("DEVICE_ID", "").upper()


def get_target_node_addresses(num_nodes: int) -> List[str]:
    """Retrieve target node addresses from environment variables."""
    return [os.getenv(f"IOT_TARGET_{i + 1}") for i in range(num_nodes)]


def validate_size_option(algo_code: str, size_option: str) -> Algorithm:
    """Validate the size option against the algorithm's available sizes."""
    algo = Algorithm[algo_code]
    if size_option not in algo.value["avail_sizes"]:
        raise ValueError(
            f"Invalid data size option: {size_option}. "
            f"Supported options: {algo.value['avail_sizes']}"
        )
    return algo


def start_iot(
    device_id: str, algo_code: str, size_option: str, iterations: int, arch_name: str
) -> None:
    """Start IoT clients and handle their lifecycle."""
    try:
        algo = validate_size_option(algo_code, size_option)
        arch = ModelArch[arch_name]

        num_nodes = int(os.getenv("NUM_IOT_TARGETS", "1"))
        target_node_addresses = get_target_node_addresses(num_nodes)
        iot_clients = []

        for i, address in enumerate(target_node_addresses):
            client_device_id = f"{device_id}-t{i + 1}" if num_nodes > 1 else device_id
            iot_client = IoTClient(
                device_id=client_device_id,
                target_address=address,
                size_option=size_option,
                algo=algo,
                iterations=iterations,
                arch=arch,
            )
            iot_clients.append(iot_client)
            iot_client.start()

        for iot_client in iot_clients:
            iot_client.join()

    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        for iot_client in iot_clients:
            iot_client.stop()


def start_edge(device_id: str) -> None:
    """Start Edge node and handle its lifecycle."""
    edge_node = EdgeNode(device_id)
    try:
        edge_node.run()
    except Exception as e:
        edge_node.logger.error(f"An error occurred: {e}")
    finally:
        edge_node.stop()


def start_cloud(device_id: str, arch_name: str) -> None:
    """Start Cloud server and handle its lifecycle."""
    cloud = CloudServer(device_id, arch=ModelArch[arch_name])
    try:
        cloud.run()
    except Exception as e:
        cloud.logger.error(f"An error occurred: {e}")
    finally:
        if cloud.data:
            cloud.print_stats()
        cloud.stop()


@click.command()
@click.option(
    "--algo-code",
    default="SW",
    help="Algorithm code (e.g., SW, FFT)",
    show_default=True,
)
@click.option(
    "--size-option",
    default=DEFAULT_DATA_SIZE_OPTION,
    help="Data size option",
    show_default=True,
)
@click.option(
    "--iterations",
    default=DEFAULT_ITERATIONS,
    type=int,
    help="Number of iterations",
    show_default=True,
)
@click.option(
    "--arch-name",
    type=click.Choice(ModelArch._member_names_, case_sensitive=False),
    prompt=True if ROLE != "EDGE" else False,
    help="Model architecture",
)
def main(algo_code: str, size_option: str, iterations: int, arch_name: str) -> None:
    """Main entry point to start IoT, Edge, or Cloud based on the ROLE environment variable."""
    try:
        if ROLE not in VALID_ROLES:
            raise ValueError(f"Invalid role: {ROLE}")
        if not DEVICE_ID:
            raise ValueError("Device ID is not set in environment variables")

        device_id = get_nid(ROLE, DEVICE_ID)

        if ROLE == "IOT":
            start_iot(
                device_id, algo_code.upper(), size_option, iterations, arch_name.upper()
            )
        elif ROLE == "EDGE":
            start_edge(device_id)
        elif ROLE == "CLOUD":
            start_cloud(device_id, arch_name.upper())
        else:
            raise ValueError(f"Invalid role: {ROLE}")

    except (ValueError, KeyboardInterrupt, SystemExit) as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
