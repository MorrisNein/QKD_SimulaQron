from time import time
from common.networking.network import setup_network
from common.networking.machine import run_nodes_auto


def main():
    n_nodes = 5
    topology_type = "star"
    network, topology_graph = setup_network(n_nodes, topology_type, keyboard_interrupt=False)

    t1 = time()

    run_nodes_auto(topology_graph)

    t2 = time()
    network.stop()
    print(f"Time for {n_nodes} nodes in {topology_type} is {round(t2 - t1, 2)} s")


if __name__ == '__main__':
    main()
