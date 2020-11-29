import sys
sys.path.append('../../')
from common.bb84.node import Node


def main():
    number_of_nodes = 10
    middle_nodes = []
    for i in range(number_of_nodes):
        node_name = 'node' + str(i)
        middle_nodes.append(Node(node_name))

    transmit_key(middle_nodes)


def transmit_key(middle_nodes):
    for i in range(len(middle_nodes)-1):
        middle_nodes[i].transmit_key(middle_nodes[i+1].name)
        middle_nodes[i+1].receive_key(middle_nodes[i].name)
    for i in range()


if __name__ == '__main__':
    main()
