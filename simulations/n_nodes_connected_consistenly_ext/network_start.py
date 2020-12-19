from networking.network import setup_network


def main():
    # Setup the network
    setup_network(4, "path", keyboard_interrupt=True)


if __name__ == '__main__':
    main()
