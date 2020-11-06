import sys
sys.path.append('../../')


def main():
    from random import getrandbits
    from common.bb84.node import Node
    from common.bb84.service import key_length_required

    quantum_protected_key = bin(getrandbits(key_length_required))[2:]
    quantum_protected_key = "0"*(key_length_required-len(quantum_protected_key)) + quantum_protected_key
    print(f"Alice's quantum protected key: {quantum_protected_key}")
    alice = Node('Alice')
    alice.transmit_key('Charlie', logging_level=1)
    alice.send_classical_bit_string('Charlie', quantum_protected_key, alice.keys['Charlie'])


if __name__ == '__main__':
    main()
