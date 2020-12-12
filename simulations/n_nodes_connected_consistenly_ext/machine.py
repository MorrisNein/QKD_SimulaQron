from common.bb84.node import Node
from time import sleep


class Machine(Node):
    def __init__(self, name: str):
        Node.__init__(self, name)

    def wait_for_a_command(self):
        while True:
            print('waiting for a command')
            command = self.receive_classical_byte_string()
            print('got a command', command)
            decoded_command = command.decode().split(' ')
            if decoded_command[0] == 'command':
                self.handle_command(decoded_command)
            sleep(0.5)

    def handle_command(self, command):
        if command[1] == 'transmit_key':
            print('transmitting key')
            self.command_transmit_key(command[2])
            print('key transmitted')
        elif command[1] == 'receive_key':
            print('receiving key')
            self.command_receive_key(command[2])
            print('key received')
        self.send_classical_byte_string('Manager', f'{self.name} free'.encode('utf-8'))

    def command_transmit_key(self, receiver):
        self.transmit_key(receiver)

    def command_receive_key(self, transmitter):
        self.receive_key(transmitter)
