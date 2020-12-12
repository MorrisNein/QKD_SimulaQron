import threading
from time import sleep, time
from common.network import setup_network
from common.bb84.node import Node
from simulations.n_nodes_connected_consistenly_ext.machine import Machine


node_availability = {}
node_manager = Node('Manager')
is_shutdown_network = False


def main():
    n_nodes = 5
    topology_type = "path"
    network = setup_network(n_nodes, topology_type, keyboard_interrupt=False)
    t1 = time()
    threads = run_nodes_path(n_nodes)
    for thread in threads:
        thread.join()
    t2 = time()
    network.stop()
    print(f"Time for {n_nodes} nodes in {topology_type} is {t2 - t1} s")


def run_nodes_path(n_nodes):
    global is_shutdown_network

    node_threads = []
    nodes = []
    for i in range(n_nodes):
        nodes.append(Machine(f"Node{i + 1}"))

    for n in nodes:
        thread = threading.Thread(target=n.wait_for_a_command)
        thread.start()
        node_threads.append(thread)
        node_availability[n.name] = 1

    # is_shutdown_network = True
    manager_thread_command = threading.Thread(target=wait_for_availability_response)
    manager_thread_response_wait = threading.Thread(target=transmit_key_path_commands, kwargs={'nodes': nodes})

    manager_thread_command.start()
    manager_thread_response_wait.start()

    threads = node_threads + [manager_thread_command, manager_thread_response_wait]

    return threads


def transmit_key_path_commands(nodes):
    global node_manager
    global is_shutdown_network
    distance = len(nodes)
    commands_to_send = []
    for i in range(distance):
        node_availability[nodes[i].name] = 0
    for i in range(0, distance):
        if i % 2 == 0 and i != distance-1:
            node_manager.send_classical_string(nodes[i].name, f'command transmit_key {nodes[i + 1].name}'.encode())
        else:
            node_manager.send_classical_string(nodes[i].name, f'command receive_key {nodes[i - 1].name}'.encode())
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
    is_shutdown_network = True
    exit()


def send_commands(commands_to_send):
    while commands_to_send:
        command = commands_to_send.pop(0).split()
        if node_availability[command[0]] == 1:
            node_availability[command[0]] = 0
            node_manager.send_classical_string(command[0], ' '.join(command[1:]).encode())
        else:
            commands_to_send.append(' '.join(command))


def wait_for_availability_response():
    # global node_availability
    # global node_manager
    # global is_keep_waiting
    print('checking availability')
    while not is_shutdown_network:
        message = node_manager.receive_classical_string().decode()
        node_availability[message.split()[0]] = 1
        sleep(1)
    else:
        print('stopped waiting')


if __name__ == '__main__':
    main()
