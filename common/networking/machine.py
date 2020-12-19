from multiprocessing import Manager
from multiprocessing.context import Process
from ast import literal_eval
from time import sleep

from common.bb84.node import Node


class Machine(Node):
    def __init__(self, name: str, machine_manager_name: str, mutex):
        Node.__init__(self, name)
        self.machine_manager_name = machine_manager_name
        self.mutex = mutex
        self.command_queue = {}

    def wait_for_a_command(self):
        self.mutex.acquire()
        self.send_classical_string(self.machine_manager_name, f'{self.name} free'.encode('utf-8'))
        self.mutex.release()

        is_waiting_for_commands = True
        while is_waiting_for_commands:
            print(f'{self.name}: waiting for a command')
            command = self.receive_classical_string()
            decoded_command = literal_eval(command.decode())
            if 'msg_type' in decoded_command and decoded_command['msg_type'] == 'command':
                print(f'{self.name}: got a command', decoded_command)
                is_waiting_for_commands = self.handle_command(decoded_command)
            sleep(0.5)

    def handle_command(self, command):
        command_cipher = command["data"]
        if command_cipher == "transmit_key":
            print(f"{self.name} transmitting key")
            self.command_transmit_key(command["partner"])
            print(f"{self.name}: key transmitted")
        elif command_cipher == "receive_key":
            print(f"{self.name}: receiving key")
            self.command_receive_key(command["partner"])
            print(f"{self.name}: key received")
        elif command_cipher == "shutdown":
            print(f"{self.name}: shutting down")
            print(f"{self.name}\"s keys: {self.keys}")
            return False

        self.mutex.acquire()
        self.send_classical_string(self.machine_manager_name, f'{self.name} free'.encode('utf-8'))
        self.mutex.release()

        return True

    def command_transmit_key(self, receiver):
        self.transmit_key(receiver)

    def command_receive_key(self, transmitter):
        self.receive_key(transmitter)


class MachineManager(Node):
    def __init__(self, name: str):
        Node.__init__(self, name)
        self.nodes_availability = {}

    def transmit_key_path_commands(self, nodes):
        distance = len(nodes)
        commands_to_send = {}

        # stage 1:
        for i in range(0, distance):
            commands_to_send[nodes[i].name] = []
            if i % 2 == 0 and i != (distance - 1):
                commands_to_send[nodes[i].name] += [self.encode_command("transmit_key", nodes[i + 1].name)]
            else:
                commands_to_send[nodes[i].name] += [self.encode_command("receive_key", nodes[i - 1].name)]

        # stage 2:
        for i in range(1, distance - 1):
            if i % 2 == 1:
                commands_to_send[nodes[i].name] += [self.encode_command("transmit_key", nodes[i + 1].name)]
            else:
                commands_to_send[nodes[i].name] += [self.encode_command("receive_key", nodes[i - 1].name)]
        self.send_commands(commands_to_send)

        # over
        assert not commands_to_send
        for n in nodes:
            commands_to_send[n.name] = [self.encode_command('shutdown')]
        self.send_commands(commands_to_send)

    @staticmethod
    def encode_command(command_cipher, partner='', executor=''):
        command = {}

        if command_cipher:
            command['data'] = command_cipher

        if partner:
            command['partner'] = partner

        if executor:
            command['executor'] = executor

        command['msg_type'] = 'command'

        return command

    # @staticmethod
    # def decode_command(command_cipher, partner='', executor=''):
    #     command = {}
    #
    #     if command_cipher:
    #         command['command'] = command_cipher
    #
    #     if partner:
    #         command['partner'] = partner
    #
    #     if executor:
    #         command['executor'] = executor
    #
    #     return str(command)

    def send_commands(self, commands_to_send):

        while commands_to_send:

            # IF (there's any node that is in commands_to_send AND the node is available):
            #   send the command immediately
            # ELSE
            #   wait for response
            for node in commands_to_send:
                if node in self.nodes_availability and self.nodes_availability[node]:
                    # if self.__check_node_availability(node, commands_to_send):
                    free_node = node
                    break
            else:
                free_node = self.wait_for_node_availability_response()

            # if we got no commands for the node, we just let it be
            if free_node not in commands_to_send:
                # if not self.__check_node_availability(free_node, commands_to_send):
                continue

            command = commands_to_send[free_node].pop(0)
            if not commands_to_send[free_node]:
                commands_to_send.pop(free_node)

            self.nodes_availability[free_node] = False
            self.send_classical_string(free_node, str(command).encode())

    # def __check_node_availability(self, node, commands_to_send):
    #     is_there_commands_for_node = node in commands_to_send
    #     is_node_available = node in self.nodes_availability and self.nodes_availability[node]
    #
    #     node_partner = commands_to_send[node][0]['partner']
    #     is_node_partner_needed = bool(node_partner)
    #     is_node_partner_available = False
    #     if is_node_partner_needed:
    #         is_node_partner_available = \
    #             node_partner in self.nodes_availability and self.nodes_availability[node_partner]
    #
    #     return \
    #         is_there_commands_for_node\
    #         and is_node_available\
    #         and (not is_node_partner_needed or is_node_partner_available)
    #

    def wait_for_node_availability_response(self):
        message = self.receive_classical_string().decode()
        node_name, is_it_free = message.split()
        if is_it_free == "free":
            # the Manager "wait for response" process says that the node is free
            self.nodes_availability[node_name] = True
            return node_name
        else:
            raise Exception(f"Manager got unexpected message: {is_it_free}")


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

