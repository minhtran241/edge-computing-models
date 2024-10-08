import os
import click
from typing import List
from dotenv import load_dotenv
from helpers.common import get_nid
from services import Algorithm, ModelArch
from services.IoTClient import IoTClient
from services.EdgeNode import EdgeNode
from services.CloudServer import CloudServer

# Constants
VALID_ROLES: List[str] = ["iot", "edge", "cloud"]
DEFAULT_ITERATIONS: int = 54
DEFAULT_DATA_SIZE_OPTION: str = "small"
EDGE_LOG_DIR: str = os.getenv("EDGE_LOG_DIR", "edge_logs")


def start_iot(
    device_id: str, algo_code: str, size_option: str, iterations: int, arch: str
) -> None:
    iot_clients: List[IoTClient] = []
    try:
        algo = Algorithm[algo_code]

        if size_option not in algo.value["avail_sizes"]:
            raise ValueError(
                f"Invalid data size option: {size_option}. Supported options: {algo.value['avail_sizes']}"
            )
        arch = ModelArch[arch]

        NUM_TARGET_NODES = int(os.getenv("NUM_IOT_TARGETS"))
        TARGET_NODE_ADDRESSES = [
            os.getenv(f"IOT_TARGET_{i+1}") for i in range(NUM_TARGET_NODES)
        ]

        if NUM_TARGET_NODES == 1:
            iot_client = IoTClient(
                device_id=device_id,
                target_address=TARGET_NODE_ADDRESSES[0],
                size_option=size_option,
                algo=algo,
                iterations=iterations,
                arch=arch,
            )
            iot_client.start_in_main_thread()
            return

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


def start_edge(device_id: str, job: str, edge_log_dir: str) -> None:
    try:
        # If log files not exists, create them. If there is content in the log files (time_stats.txt and sent_data.txt), remove content
        if not os.path.exists(edge_log_dir):
            os.makedirs(edge_log_dir)
        else:
            for f in ["time_stats.txt", "sent_data.txt"]:
                with open(f"{edge_log_dir}/{f}", "w") as file:
                    file.write("")
        edge_node = EdgeNode(device_id, job=job, edge_log_dir=edge_log_dir)
        edge_node.run()
    except (KeyboardInterrupt, SystemExit, Exception) as e:
        if isinstance(e, Exception):
            edge_node.logger.error(f"An error occurred: {e}")
        edge_node.stop()


def start_cloud(device_id: str, arch: str) -> None:
    try:
        arch: ModelArch = ModelArch[arch]
        cloud = CloudServer(device_id, arch=arch)
        cloud.run()
    except (KeyboardInterrupt, SystemExit, Exception) as e:
        if isinstance(e, Exception):
            cloud.logger.error(f"An error occurred: {e}")
        if len(cloud.data) > 0:
            cloud.print_stats()
        cloud.stop()


# python3 trigger.py cloud 1 --algo-code ocr --size-option small --iterations 10 --arch cloud
# python3
@click.command()
@click.argument("role", type=click.Choice(VALID_ROLES, case_sensitive=False))
@click.argument("device_id")
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
    "--arch",
    help="Model architecture",
    type=click.Choice(ModelArch._member_names_, case_sensitive=False),
)
@click.option(  # For edge node
    "--edge-job",
    help="Edge job type",
    type=click.Choice(["recv", "send"], case_sensitive=False),
)
def main(role, device_id, algo_code, size_option, iterations, arch, edge_job):
    load_dotenv()

    device_id = get_nid(role, device_id)

    if role == "iot":
        start_iot(
            device_id=device_id,
            algo_code=algo_code.upper(),
            size_option=size_option,
            iterations=iterations,
            arch=arch.upper(),
        )
    elif role == "cloud":
        start_cloud(device_id, arch.upper())
    elif role == "edge":
        edge_log_dir = (
            f"{EDGE_LOG_DIR}/{device_id}/{algo_code}-{size_option}-{iterations}"
        )
        start_edge(device_id, edge_job, edge_log_dir)
    else:
        click.echo(f"Unknown role: {role}")


if __name__ == "__main__":
    main()
