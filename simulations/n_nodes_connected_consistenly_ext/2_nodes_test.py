import threading
from common.bb84.node import Node
from simulations.n_nodes_connected_consistenly_ext.machine import Machine

node_threads = []
nodes = [Machine("Alice"), Machine("Bob")]
for i in range(2):
    node_threads.append(threading.Thread(target=nodes[i].wait_for_a_command))
    node_threads[i].start()
    print(str(i), 'thread started')
node_manager = Node('Manager')
node_manager.send_classical_byte_string('Alice', 'command transmit_key Bob'.encode('utf-8'))
print('first command sent')
node_manager.send_classical_byte_string('Bob', 'command receive_key Alice'.encode('utf-8'))
print('second command sent')