import sys
sys.path.append('../../')


def main():
    from common.bb84.node import Node

    bob = Node('Bob')
    # Alice and Charlie make their key
    bob.receive_key('Charlie')
    quantum_protected_key = bob.receive_classical_bit_string(key=bob.keys['Charlie'])
    print(f"Bob's quantum protected key: {quantum_protected_key}")


if __name__ == '__main__':
    main()
