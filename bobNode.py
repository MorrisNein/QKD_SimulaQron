from node import Node


def main():
    bob = Node('Bob')
    # Alice and Charlie make their key
    bob.receive_key('Charlie')

    # Charlie mixes Alice's and Bob's keys and sends the mix to Bob

    bob.keys['Alice-Charlie'] = bob.receive_classical_bit_string()

    bob.mix_keys(bob.keys['Alice-Charlie'], bob.keys['Charlie'], 'Alice')

    print("Bob received Alice's key", bob.keys['Alice'])


if __name__ == '__main__':
    main()
