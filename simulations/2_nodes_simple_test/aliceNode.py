import sys
import os

sys.path.append('../../')
sys.path.append(os.getcwd())


def main():
    import time as t
    from qkd.bb84.node import Node
    alice = Node('Alice')

    t1 = t.time()
    alice.transmit_key('Bob', logging_level=2)
    t2 = t.time()

    bob_key = alice.receive_classical_bit_string()
    print('Is Bob\'s key the same as Alice\'s?')
    print((bob_key == alice.keys['Bob']))
    print(f'QKD run {round(t2-t1, 2)} s')


if __name__ == '__main__':
    main()
