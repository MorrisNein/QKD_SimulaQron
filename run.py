from time import time
from qkd.networking.network import setup_network
from qkd.networking.routing import run_nodes_path


def main():
    n_nodes = 2
    topology_type = "path"
    network, _ = setup_network(n_nodes, topology_type, keyboard_interrupt=False)
    t1 = time()

    run_nodes_path(n_nodes)

    t2 = time()
    network.stop()
    print(f"Time for {n_nodes} nodes in {topology_type} is {round(t2 - t1, 2)} s")


if __name__ == '__main__':
    main()
