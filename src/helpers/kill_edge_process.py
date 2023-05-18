import os

from config import EDGE_KILL_COMMAND


def kill_edge_processes() -> None:
    try:
        os.system(EDGE_KILL_COMMAND)
        print(" ** Killed edge processes ** ")
    except Exception as e:
        print(f"Error while killing edge processes: {e}")
