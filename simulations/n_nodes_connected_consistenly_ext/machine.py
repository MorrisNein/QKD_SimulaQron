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
                if decoded_command[1] == 'transmit_key':
                    self.transmit_key(decoded_command[2])
                elif decoded_command[1] == 'receive_key':
                    self.receive_key(decoded_command[2])
            sleep(1)
