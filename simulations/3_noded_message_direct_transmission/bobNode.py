import sys

sys.path.append('../../')


def main():
    from common.bb84.node import Node

    bob = Node('Bob')
    # key_length = bob.receive_classical_int('Alice')
    key_length = 40
    # Alice and Charlie make their key
    bob.receive_key('Charlie', key_length_required=key_length)
    encoded_message = bob.receive_classical_string(key=bob.keys['Charlie'])
    message = ''
    for i in encoded_message:
        message += chr(i)
    # message = encoded_message.decode('utf-8')
    print(f"Bob received message : {message}")


if __name__ == '__main__':
    main()
