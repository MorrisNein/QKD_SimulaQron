import sys
sys.path.append('../../')


def main():
    from common.bb84.node import Node

    bob = Node('Bob')
    # Alice and Charlie make their key
    bob.receive_key('Charlie')

    # Charlie mixes Alice's and Bob's keys and sends the mix to Bob

    bob.keys['Alice-Charlie'] = bob.receive_classical_bit_string()

    print(f"Bob received mixed key: {bob.keys['Alice-Charlie']}\n")

    bob.mix_keys(bob.keys['Alice-Charlie'], bob.keys['Charlie'], 'Alice')

    print(f"Bob received Alice's key: {bob.keys['Alice']}\n")


if __name__ == '__main__':
    main()
