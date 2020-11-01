import newNode


def main():
    alice = newNode.Node()
    alice.initialize('Alice')
    alice.transmit_key('Charlie')


if __name__ == '__main__':
    main()
