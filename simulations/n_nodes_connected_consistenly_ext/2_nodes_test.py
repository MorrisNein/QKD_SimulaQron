import threading
from time import sleep
from common.bb84.node import Node
from simulations.n_nodes_connected_consistenly_ext.machine import Machine


node_availability = {}
node_manager = Node('Manager')


def main():
    global node_availability
    global node_manager
    node_threads = []
    nodes = []
    for i in range(4):
        nodes.append(Machine(str(i+1)))
    #nodes = [Machine("Alice"), Machine("Bob")]
    for i in range(len(nodes)):
        node_threads.append(threading.Thread(target=nodes[i].wait_for_a_command))
        node_threads[i].start()
        print(str(i), 'thread started')
        node_availability[nodes[i].name] = 1
    threading.Thread(target=transmit_key_command, kwargs={'nodes': nodes}).start()
    threading.Thread(target=get_availability_response).start()
'''    node_manager.send_classical_byte_string('Alice', 'command transmit_key Bob'.encode('utf-8'))
    print('first command sent')
    node_manager.send_classical_byte_string('Bob', 'command receive_key Alice'.encode('utf-8'))
    print('second command sent')'''


def transmit_key_command(nodes):
    global node_manager
    distance = len(nodes)
    commands_to_be_sent = []
    for i in range(distance):
        node_availability[nodes[i].name] = 0
    for i in range(0, distance):
        if i % 2 == 0:
            node_manager.send_classical_byte_string(nodes[i].name, f'command transmit_key {nodes[i+1].name}'.encode())
            print('com sent')
        else:
            node_manager.send_classical_byte_string(nodes[i].name, f'command receive_key {nodes[i-1].name}'.encode())
            print('com sent')
    for i in range(1, distance-1):
        if i % 2 == 1:
            commands_to_be_sent.append(f'{nodes[i].name} command transmit_key {nodes[i+1].name}')
        else:
            commands_to_be_sent.append(f'{nodes[i].name} command receive_key {nodes[i-1].name}')
    while len(commands_to_be_sent) != 0:
        for i in range(len(commands_to_be_sent)):
            command = commands_to_be_sent[i].split()
            if node_availability[command[0]] == 1:
                node_availability[command[0]] = 0
                node_manager.send_classical_byte_string(command[0], ' '.join(command[1:]).encode())


def get_availability_response():
    global node_availability
    global node_manager
    print('checking availability')
    while 1:
        message = node_manager.receive_classical_byte_string().decode()
        node_availability[message.split()[0]] = 1
        sleep(0.1)


if __name__ == '__main__':
    main()
