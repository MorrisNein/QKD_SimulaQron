from multiprocessing import Manager
from multiprocessing.context import Process

from common.networking.machine import Machine, MachineManager

def run_nodes_path(n_nodes):

    machine_manager_name = 'Manager'
    node_procs = []
    machines = []
    processes_manager = Manager()
    mutex = processes_manager.Lock()

    for i in range(n_nodes):
        # Creating machine
        machine = Machine(f"Node{i + 1}", machine_manager_name, mutex)
        machines.append(machine)

        # Creating and starting process
        proc = Process(target=machine.wait_for_a_command)
        proc.start()
        node_procs.append(proc)

    node_manager = MachineManager(machine_manager_name)
    manager_response_wait_proc = Process(target=node_manager.transmit_key_path_commands, kwargs={'nodes': machines})

    manager_response_wait_proc.start()
    node_procs += [manager_response_wait_proc]

    for p in node_procs:
        p.join()


def run_nodes_auto(topology_graph):

    machine_manager_name = 'Manager'
    node_procs = []
    machines = []
    processes_manager = Manager()
    mutex = processes_manager.Lock()

    for node_name in topology_graph.nodes:
        # Creating machine
        machine = Machine(node_name, machine_manager_name, mutex)
        machines.append(machine)

        # Creating and starting process
        proc = Process(target=machine.wait_for_a_command)
        proc.start()
        node_procs.append(proc)

    node_manager = MachineManager(machine_manager_name)
    manager_response_wait_proc = Process(target=node_manager.transmit_key_auto_commands,
                                         kwargs={'topology_graph': topology_graph})

    manager_response_wait_proc.start()
    node_procs += [manager_response_wait_proc]

    for p in node_procs:
        p.join()

