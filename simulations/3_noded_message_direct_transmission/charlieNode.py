import sys

sys.path.append('../../')


def main():
    from common.bb84.node import Node

    charlie = Node('Charlie')
    # key_length = charlie.receive_classical_int('Alice')
    key_length = 40
    # Alice sends key
    charlie.receive_key('Alice', key_length_required=key_length, logging_level=1)
    encoded_message = charlie.receive_classical_byte_string(key=charlie.keys['Alice'])
    # print(f"Charlie's quantum protected key: {quantum_protected_key}")

    charlie.transmit_key('Bob', key_length_required=key_length)
    charlie.send_classical_byte_string('Bob', encoded_message, charlie.keys['Bob'])


if __name__ == '__main__':
    main()
