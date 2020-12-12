from simulaqron.network import Network


def main():
    # Setup the network
    nodes = ["1", "2", "3", "4", "Manager"]
    topology = {"1": ["2"], "2": ["1", "3"], "3": ["2", "4"], "4": ["3"], "Manager": []}

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
    # Can we enter the nodes simulations here??? YES, BUT ONLY IN PARALLEL!
    # ============================================= #
    """

    network.stop()  # not necessary
    print("Network has stopped!")


if __name__ == '__main__':
    main()
