from common.bb84.node import Node
from time import sleep


class Machine(Node):
    def __init__(self, name: str, machine_manager_name: str, mutex):
        Node.__init__(self, name)
        self.machine_manager_name = machine_manager_name
        self.mutex = mutex

    def wait_for_a_command(self):
        self.mutex.acquire()
        self.send_classical_string(self.machine_manager_name, f'{self.name} free'.encode('utf-8'))
        self.mutex.release()

        is_still_waiting = True
        while is_still_waiting:
            print(f'{self.name}: waiting for a command')
            command = self.receive_classical_string()
            print(f'{self.name}: got a command', command)
            decoded_command = command.decode().split(' ')
            if decoded_command[0] == 'command':
                is_still_waiting = self.handle_command(decoded_command)
            sleep(0.5)

    def handle_command(self, command):
        if command[1] == 'transmit_key':
            print(f'{self.name} transmitting key')
            self.command_transmit_key(command[2])
            print(f'{self.name}: key transmitted')
        elif command[1] == 'receive_key':
            print(f'{self.name}: receiving key')
            self.command_receive_key(command[2])
            print(f'{self.name}: key received')
        elif command[1] == 'shutdown':
            print(f'{self.name}: shutting down')
            print(f'{self.name}\'s keys: {self.keys}')
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
            if i % 2 == 0 and i != distance-1:
                commands_to_send[nodes[i].name] += [f'command transmit_key {nodes[i + 1].name}']
            else:
                commands_to_send[nodes[i].name] += [f'command receive_key {nodes[i - 1].name}']

        # stage 2:
        for i in range(1, distance - 1):
            if i % 2 == 1:
                commands_to_send[nodes[i].name] += [f'command transmit_key {nodes[i + 1].name}']
            else:
                commands_to_send[nodes[i].name] += [f'command receive_key {nodes[i - 1].name}']
        self.send_commands(commands_to_send)

        # over
        assert not commands_to_send
        for n in nodes:
            commands_to_send[n.name] = ['command shutdown']
        self.send_commands(commands_to_send)

    def send_commands(self, commands_to_send):

        while commands_to_send:

            # IF (there's any node that is in commands_to_send AND the node is available):
            #   send the command immediately
            # ELSE
            #   wait for response
            for node in commands_to_send:
                if node in self.nodes_availability and self.nodes_availability[node]:
                    free_node = node
                    break
            else:
                free_node = self.wait_for_node_availability_response()

            # if we got no commands for the node, we just let it be
            if free_node not in commands_to_send:
                continue

            command = commands_to_send[free_node].pop(0)
            if not commands_to_send[free_node]:
                commands_to_send.pop(free_node)

            self.nodes_availability[free_node] = False
            self.send_classical_string(free_node, command.encode())

    def wait_for_node_availability_response(self):
        message = self.receive_classical_string().decode()
        node_name, is_it_free = message.split()
        if is_it_free == "free":
            # the Manager "wait for response" process says that the node is free
            self.nodes_availability[node_name] = True
            return node_name
        else:
            raise Exception(f"Manager got unexpected message: {is_it_free}")