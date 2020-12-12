import threading
from time import sleep
from common.bb84.node import Node
from simulations.n_nodes_connected_consistenly_ext.machine import Machine

node_availability = {}
node_manager = Node('Manager')
mutex = threading.Lock()
global is_keep_waiting


def main():
    # global node_availability
    # global node_manager
    global is_keep_waiting

    node_threads = []
    nodes = []
    for i in range(4):
        nodes.append(Machine(str(i + 1)))

    for i in range(len(nodes)):
        node_threads.append(threading.Thread(target=nodes[i].wait_for_a_command))
        node_threads[i].start()
        print(str(i), 'thread started')

        node_availability[nodes[i].name] = 1
    is_keep_waiting = True
    threading.Thread(target=wait_for_availability_response).start()
    threading.Thread(target=transmit_key_path_commands, kwargs={'nodes': nodes}).start()

    # node_manager.send_classical_byte_string('Alice', 'command transmit_key Bob'.encode('utf-8'))
    # print('first command sent')
    # node_manager.send_classical_byte_string('Bob', 'command receive_key Alice'.encode('utf-8'))
    # print('second command sent')


def transmit_key_path_commands(nodes):
    global node_manager
    global is_keep_waiting
    distance = len(nodes)
    commands_to_send = []
    for i in range(distance):
        node_availability[nodes[i].name] = 0
    for i in range(0, distance):
        if i % 2 == 0:
            node_manager.send_classical_byte_string(nodes[i].name, f'command transmit_key {nodes[i + 1].name}'.encode())
            print('com sent')
        else:
            node_manager.send_classical_byte_string(nodes[i].name, f'command receive_key {nodes[i - 1].name}'.encode())
            print('com sent')
    for i in range(1, distance - 1):
        if i % 2 == 1:
            commands_to_send.append(f'{nodes[i].name} command transmit_key {nodes[i + 1].name}')
        else:
            commands_to_send.append(f'{nodes[i].name} command receive_key {nodes[i - 1].name}')
    send_commands(commands_to_send)

    assert not commands_to_send
    for n in nodes:
        commands_to_send.append(f'{n.name} command shutdown')
    send_commands(commands_to_send)
    is_keep_waiting = False
    exit()


def send_commands(commands_to_send):
    while commands_to_send:
        command = commands_to_send.pop(0).split()
        if node_availability[command[0]] == 1:
            node_availability[command[0]] = 0
            node_manager.send_classical_byte_string(command[0], ' '.join(command[1:]).encode())
        else:
            commands_to_send.append(' '.join(command))


def wait_for_availability_response():
    # global node_availability
    # global node_manager
    # global is_keep_waiting
    print('checking availability')
    while is_keep_waiting:
        message = node_manager.receive_classical_string().decode()
        node_availability[message.split()[0]] = 1
        sleep(1)
    else:
        print('stopped waiting')


if __name__ == '__main__':
    main()
