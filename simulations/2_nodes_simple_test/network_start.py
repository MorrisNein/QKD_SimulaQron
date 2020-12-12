from simulaqron.network import Network
import networkx as nx


def main():
    # Setup the network
    nodes = ["Alice", "Bob"]
    g = nx.path_graph(nodes)
    topology = {n: list(g.neighbors(n)) for n in nodes}

    network = Network(name="default",
                      nodes=nodes,
                      topology=topology,
                      force=True)

    # Start the network
    network.start(wait_until_running=True)

    print(f"The network has started with topology: \n{network.topology}\n")

    input("Press Enter to stop the network... \n")

    """
    # ============================================= #
    # Can we enter the nodes simulations here??? YES, BUT ONLY IN PARALLEL!
    # ============================================= #
    """

    network.stop()  # not necessary
    print("Network has stopped!")


if __name__ == '__main__':
    main()
