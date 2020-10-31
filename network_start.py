import time

from simulaqron.network import Network


def main():
    # Setup the network
    network_config_file = \
        "custom_network.json"
    nodes = ["Alice", "Bob", "Charlie"]
    topology = {"Alice": ["Charlie"], "Bob": ["Charlie"], "Charlie": ["Alice", "Bob"]}
    # network = Network(new=False, name="test", network_config_file=network_config_file, nodes=nodes, topology=topology)
    network = Network(name="default",
                      nodes=nodes,
                      topology=topology,
                      network_config_file=network_config_file,
                      force=True)

    # Start the network
    network.start(wait_until_running=True)

    time.sleep(180)

    input("Press Enter to stop the network... \n")

    """
    # ============================================= #
    # Can we enter the nodes code here??? YES, BUT ONLY IN PARALLEL!
    # ============================================= #
    """

    network.stop()  # not necessary
    print("Network has stopped!")


if __name__ == '__main__':
    main()
