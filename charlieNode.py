from node import Node


def main():
    charlie = Node('Charlie')
    # Alice sends key_1
    charlie.receive_key('Alice')
    charlie.transmit_key('Bob')

    charlie.mix_keys(charlie.keys['Alice'], charlie.keys['Bob'], 'Alice-Bob')
    charlie.send_classical_bit_string('Bob', charlie.keys['Alice-Bob'])


if __name__ == '__main__':
    main()
