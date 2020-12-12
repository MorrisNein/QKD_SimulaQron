# import networkx as nx
# import threading
# from simulaqron.network import Network
# from time import sleep
# from common.bb84.node import Node
# from simulations.n_nodes_connected_consistenly_ext.machine import Machine
#
#
# node_availability = {}
# node_manager = Node('Manager')
# network = None
#
#
# def main():
#     n_nodes = 4
#     topology_type = "path"
#     setup_network(n_nodes, topology_type)
#     run_nodes_path(n_nodes)
#
#
# def setup_network(n_nodes, topology_type, is_manager_needed=True):
#     # Setup the network
#     global network
#
#     G = nx.Graph()
#
#     nodes_QKD_num = n_nodes
#     nodes_QKD = (f"Node{i+1}" for i in range(nodes_QKD_num))
#
#     topologies_available = {"path": nx.path_graph}
#
#     if topology_type not in topologies_available:
#         raise Exception(f"Inappropriate topology type. Please select one of the followings: {topologies_available}")
#
#     G_new = topologies_available[topology_type](nodes_QKD)
#     G.add_edges_from(G_new.edges)
#
#     if is_manager_needed:
#         G.add_node("Manager")
#
#     topology = {n: list(G.neighbors(n)) for n in G.nodes}
#
#     network = Network(name="default",
#                       nodes=nodes_QKD,
#                       topology=topology,
#                       force=True)
#
#     # Start the network
#     network.start(wait_until_running=True)
#
#     print(f"The network has started with topology: \n{network.topology}\n")
#
#     # input("Press Enter to stop the network... \n")
#
#     """
#     # ============================================= #
#     # Can we enter the nodes simulations here??? YES, BUT ONLY IN PARALLEL!
#     # ============================================= #
#     """
#
#     # network.stop()  # not necessary
#     # print("Network has stopped!")
#
#
# def run_nodes_path(n_nodes):
#     global node_availability
#     global node_manager
#     node_threads = []
#     nodes = []
#     for i in range(4):
#         nodes.append(Machine(f"Node{i+1}"))
#     # nodes = [Machine("Alice"), Machine("Bob")]
#     for i in range(len(nodes)):
#         node_threads.append(threading.Thread(target=nodes[i].wait_for_a_command))
#         node_threads[i].start()
#         print(str(i), 'thread started')
#         node_availability[nodes[i].name] = 1
#     threading.Thread(target=transmit_key_command, kwargs={'nodes': nodes}).start()
#     threading.Thread(target=get_availability_response).start()
#
#
# def transmit_key_command(nodes):
#     global node_manager
#     distance = len(nodes)
#     commands_to_be_sent = []
#     for i in range(distance):
#         node_availability[nodes[i].name] = 0
#     for i in range(0, distance):
#         if i % 2 == 0:
#             node_manager.send_classical_byte_string(nodes[i].name, f'command transmit_key {nodes[i + 1].name}'.encode())
#             print('com sent')
#         else:
#             node_manager.send_classical_byte_string(nodes[i].name, f'command receive_key {nodes[i - 1].name}'.encode())
#             print('com sent')
#     for i in range(1, distance - 1):
#         if i % 2 == 1:
#             commands_to_be_sent.append(f'{nodes[i].name} command transmit_key {nodes[i + 1].name}')
#         else:
#             commands_to_be_sent.append(f'{nodes[i].name} command receive_key {nodes[i - 1].name}')
#     while len(commands_to_be_sent) != 0:
#         for i in range(len(commands_to_be_sent)):
#             command = commands_to_be_sent[i].split()
#             if node_availability[command[0]] == 1:
#                 node_availability[command[0]] = 0
#                 node_manager.send_classical_byte_string(command[0], ' '.join(command[1:]).encode())
#
#
# def get_availability_response():
#     global node_availability
#     global node_manager
#     print('checking availability')
#     while 1:
#         message = node_manager.receive_classical_byte_string().decode()
#         node_availability[message.split()[0]] = 1
#         sleep(0.1)
#
#
# if __name__ == '__main__':
#     main()
#
