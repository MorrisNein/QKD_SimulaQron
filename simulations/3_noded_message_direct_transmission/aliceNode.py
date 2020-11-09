import sys
sys.path.append('../../')


def main():
    from common.bb84.node import Node
    message = 'Hello'
    byte_message = message.encode('utf-8')
    key_length_required = 8*len(byte_message)
    alice = Node('Alice')
    #alice.send_classical_int('Charlie', msg=key_length_required)
    #alice.send_classical_int('Bob', msg=key_length_required)
    alice.transmit_key('Charlie', key_length_required=key_length_required, logging_level=1)

    alice.send_classical_byte_string('Charlie', byte_message, alice.keys['Charlie'])


if __name__ == '__main__':
    main()
