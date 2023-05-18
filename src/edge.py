from src.helpers.kill_edge_process import kill_edge_processes
from src.search.searches import run_searches


if __name__ == "__main__":
    print(" ** Starting process... ** ")

    try:
        run_searches()
    except KeyboardInterrupt:
        print("\n\n ** Process interrupted by user. **\n")
        kill_edge_processes()
        exit()
