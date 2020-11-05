from simulaqron.network import Network


def main():
    # Setup the network
    nodes = ["Alice", "Bob", "Charlie"]
    topology = {"Alice": ["Charlie"], "Bob": ["Charlie"], "Charlie": ["Alice", "Bob"]}

    network = Network(name="default",
                      nodes=nodes,
                      topology=topology,
                      force=True)

    # Start the network
    network.start(wait_until_running=True)

    print(f"The network has started with topology: \n{network.topology}\n")

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
