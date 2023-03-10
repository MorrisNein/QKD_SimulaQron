import sys
sys.path.append('../../')


def main():
    from qkd.bb84.node import Node

    alice = Node('Alice')
    alice.transmit_key('Charlie')
    # Alice then just chills until Bob receives the mixed key from Charlie.
    # Then Bob knows Alice-Charlie key and Alice can encrypt her message with it


if __name__ == '__main__':
    main()
