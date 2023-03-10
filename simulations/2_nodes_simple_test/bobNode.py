import sys
import os

sys.path.append('../../')
sys.path.append(os.getcwd())


def main():
    from qkd.bb84.node import Node
    bob = Node('Bob')

    bob.receive_key('Alice', logging_level=2)
    bob.send_classical_bit_string('Alice', bob.keys['Alice'])


if __name__ == '__main__':
    main()
