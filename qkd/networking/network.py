import networkx as nx
from simulaqron.network import Network
from qkd.config import default_topology_type, default_n_nodes


def setup_network(
    n_nodes=default_n_nodes, topology_type=default_topology_type,
    is_manager_needed=True, keyboard_interrupt=False):

    # Setup the network
    G = nx.Graph()

    nodes_QKD_num = n_nodes
    nodes_QKD = (f"Node{i+1}" for i in range(nodes_QKD_num))

    topologies_available = {
        "path": nx.path_graph,
        "star": nx.star_graph,
        "cycle": nx.cycle_graph,
    }

    if topology_type not in topologies_available:
        raise Exception(f"Inappropriate topology type. Please select one of the followings: {topologies_available}")

    G_new = topologies_available[topology_type](nodes_QKD)
    G.add_edges_from(G_new.edges)

    if is_manager_needed:
        G.add_node("Manager")

    topology = {n: list(G.neighbors(n)) for n in G.nodes}

    network = Network(name="default",
                      nodes=G.nodes,
                      topology=topology,
                      force=True,
                      )

    # Start the network
    network.start(wait_until_running=True)

    print(f"The network has started with topology: \n{network.topology}\n")

    if keyboard_interrupt:
        input("Press Enter to stop the network... \n")

    """
    # ============================================= #
    # Can we enter the nodes simulations here??? YES, BUT ONLY IN PARALLEL!
    # ============================================= #
    """

    if keyboard_interrupt:
        network.stop()  # not necessary
        print("Network has stopped!")
        return

    G.remove_node("Manager")
    return network, G
