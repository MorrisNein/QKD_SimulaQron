import newNode


def main():
    bob = newNode.Node()
    bob.initialize('Bob')
    charlie_key = bob.transmit_key('Charlie')
    alice_key = bob.decode_public_key(charlie_key)
    print("bob received alice's key", alice_key)


if __name__ == '__main__':
    main()
