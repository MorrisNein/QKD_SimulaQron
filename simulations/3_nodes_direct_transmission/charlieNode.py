import sys
sys.path.append('../../')


def main():
    from common.bb84.node import Node

    charlie = Node('Charlie')
    logging_level = 2
    # Alice sends key
    charlie.receive_key('Alice', logging_level=logging_level)
    quantum_protected_key = charlie.receive_classical_bit_string(key=charlie.keys['Alice'])
    print(f"Charlie's quantum protected key: {quantum_protected_key}")

    charlie.transmit_key('Bob', logging_level=logging_level)
    charlie.send_classical_bit_string('Bob', quantum_protected_key, charlie.keys['Bob'])


if __name__ == '__main__':
    main()
