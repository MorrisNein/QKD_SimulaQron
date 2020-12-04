import sys
sys.path.append('../../')


def main():
    from common.bb84.node import Node
    bob = Node('Bob')
    # bob.send_classical_bit_string('Alice', '101')
    bob.receive_key('Alice', logging_level=0)
    bob.send_classical_bit_string('Alice', bob.keys['Alice'])


if __name__ == '__main__':
    main()
