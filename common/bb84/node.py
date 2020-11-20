import time
import random
from textwrap import dedent
from cqc.pythonLib import CQCConnection, qubit, CQCNoQubitError
from common.bb84.service import decode_bytes_msg_to_bit_string, encode_bit_string_to_bytes_msg,\
    default_key_length_required, default_key_message_length, xor_bit_strings, default_g_q


class Node(object):

    def __init__(self, name):
        self.name = name
        self.keys = {}

    def transmit_key(self, receiver: str, key_length_required: int = default_key_length_required,
                     g_q: int = default_g_q, logging_level: int = 1):
        """
        Starts quantum key distribution between current node and the receiver node.
        The receiver node must run function receive_key simultaneously.

        :param receiver:
            Name of the receiver node specified in the network topology.
        :param key_length_required:
            Required key length in bits. By default the value is taken from bb84.service.
            Must be the same value, as the receiver got in receive_key.
        :param logging_level:
            0 - mute;
            1 - final sifted key;
            2 - every sifting iteration result.
        :param g_q:
            Quantum channel gain. Float in range [0, 1].
            By default the value is taken from bb84.service.
            The param is needed ONLY to estimate optimal sifting iterations limit.
        :return:
        """

        key_message_length = default_key_message_length
        sifting_iterations_limit = int(key_length_required / key_message_length / g_q * 3 + 3)

        # Initialize the connection
        with CQCConnection(self.name) as Me:

            sifted_key = ''
            is_key_length_reached = False

            # Generate a raw_key_str in random basis
            for sifting_iteration in range(sifting_iterations_limit):
                raw_key_str = ''
                basis_changed_positions = []

                for i in range(key_message_length):
                    # ================= Raw key message =================
                    # Create a qubit in a current node
                    q = qubit(Me)  # CQC

                    # Encode the qubit by random number
                    raw_key_str += str(random.randint(0, 1))
                    if int(raw_key_str[i]):
                        q.X()

                    # Choose random basis to send
                    if random.randint(0, 1):
                        basis_changed_positions += [i]
                        q.H()
                        raw_key_str += "1"
                    else:
                        raw_key_str += "0"

                    # Send qubit to receiver
                    try:
                        Me.sendQubit(q, receiver)  # CQC1
                    except CQCNoQubitError:
                        print("ERROR! The number of qubits expired!\n"
                              "Please increase the qubits number in config and restart the simulation.")
                        time.sleep(0.2)
                        Me.sendQubit(q, receiver)  # CQC1

                if logging_level >= 2:
                    print("====================================================\n"
                          "Sifting iteration {}\n".format(sifting_iteration))

                # ================= Raw key adjustment =================
                # Receive positions measured by other node...
                received_key_positions_o = list(self.receive_classical_int_list())  # CQC2
                # ... and keep only the same positions of key and basis
                raw_key_str = ''.join([raw_key_str[pos] for pos in received_key_positions_o])
                basis_changed_positions = [pos for pos in basis_changed_positions if pos in received_key_positions_o]

                # ================= Sifting messages =================
                # Get other node's positions of changed basis
                basis_changed_positions_o = self.receive_classical_int_list()  # CQC3
                # Send the changed basis positions
                self.send_classical_int_list(receiver, basis_changed_positions)  # CQC4

                if logging_level >= 2:
                    bases_str = "".join(
                        [str(int(i in basis_changed_positions)) for i in range(len(raw_key_str))]
                    )
                    bases_str_o = "".join(
                        [str(int(i in basis_changed_positions_o)) for i in range(len(raw_key_str))]
                    )
                    print(dedent(
                        f"""
                        {self.name}'s key: {raw_key_str}
                        {self.name}'s basis: {bases_str}
                        {self.name} received {receiver}'s basis: {bases_str_o}
                        {self.name}'s basis_changed_positions: {basis_changed_positions}
                        {self.name} knows that key positions received by {receiver} are: {received_key_positions_o}
                        """))

                # ================= Sifting =================
                for i, pos in enumerate(received_key_positions_o):
                    # XNOR: true if position is in both lists or neither of them
                    # We do not use bases_str and bases_str_o
                    # as their main purpose is logging message.
                    if not ((pos in basis_changed_positions) ^ (pos in basis_changed_positions_o)):
                        sifted_key += raw_key_str[i]

                    # ================= Break check =================
                    if len(sifted_key) >= key_length_required:
                        is_key_length_reached = True
                        break
                if is_key_length_reached:
                    break
            else:
                print("Iterations limit expired!")

            # ================= Sifted key report =================
            if logging_level >= 1:
                print(f"{self.name}'s sifted key to {receiver}: {sifted_key}")

        self.keys[receiver] = sifted_key
        return sifted_key

    def receive_key(self, transmitter: str, key_length_required: int = default_key_length_required,
                    g_q: int = default_g_q, logging_level: int = 1):
        """
        Receiver part of quantum key distribution.
        The transmitter node must run function transmit_key simultaneously.

        :param transmitter:
            Name of the receiver node specified in the network topology.
        :param key_length_required:
            Required key length in bits. By default the value is taken from bb84.service.
            Must be the same value, as the receiver got in receive_key.
        :param g_q:
            Quantum channel gain. Float in range [0, 1].
            By default the value is taken from bb84.service.
            The param is needed to estimate optimal sifting iterations limit.
        :param logging_level:
            0 - mute;
            1 - final sifted key;
            2 - every sifting iteration result.
        :return:
        """

        key_message_length = default_key_message_length
        sifting_iterations_limit = int(key_length_required / key_message_length / g_q * 3 + 3)

        with CQCConnection(self.name) as Me:

            sifted_key = ''
            is_key_length_reached = False

            # Generate a raw_key_str in random basis
            for sifting_iteration in range(sifting_iterations_limit):

                raw_key_str = ''
                basis_changed_positions = []
                received_key_positions = []

                for i in range(key_message_length):
                    # ================= Raw key message =================
                    q = Me.recvQubit()  # CQC1

                    # Here we insert the loss by quantum channel gain < 1.
                    # If g_q is less or equal than a random uniform number [0,1],
                    # then the next iteration is being started.
                    if g_q <= random.random():
                        q.release()
                        continue

                    # Remember current position to notify transmitter that it was received properly
                    received_key_positions += [i]

                    # Choose random basis to measure the received qubit
                    if random.randint(0, 1):
                        basis_changed_positions += [i]
                        q.H()
                    raw_key_str += str(q.measure())

                # ================= Raw key adjustment =================
                self.send_classical_int_list(transmitter, received_key_positions)  # CQC2

                # ================= Sifting messages =================
                # Send the node's positions of changed basis
                self.send_classical_int_list(transmitter, basis_changed_positions)  # CQC3
                # Get other node's positions of changed basis
                basis_changed_positions_o = self.receive_classical_int_list()  # CQC4

                # ================= Logging =================
                if logging_level >= 2:
                    bases_str = "".join(
                        [str(int(i in basis_changed_positions)) for i in range(len(raw_key_str))]
                    )

                    bases_str_o = "".join(
                        [str(int(i in basis_changed_positions_o)) for i in range(len(raw_key_str))]
                    )
                    print(dedent(
                        f"""
                        {self.name}'s key: {raw_key_str}
                        {self.name}'s basis: {bases_str}
                        {self.name} received {transmitter}'s basis: {bases_str_o}
                        {self.name}'s basis_changed_positions: {basis_changed_positions}
                        """))

                # ================= Sifting =================
                for i, pos in enumerate(received_key_positions):
                    # XNOR: true if position is in both lists or neither of them
                    # We do not use bases_str and bases_str_o
                    # as their main purpose is logging message.
                    if not ((pos in basis_changed_positions) ^ (pos in basis_changed_positions_o)):
                        sifted_key += raw_key_str[i]

                    # ================= Break check =================
                    if len(sifted_key) >= key_length_required:
                        is_key_length_reached = True
                        break
                if is_key_length_reached:
                    break
            else:
                print("Iterations limit expired!")

            # ================= Sifted key report =================
            if logging_level >= 1:
                print(f"{self.name}'s sifted key to {transmitter}: {sifted_key}")

        self.keys[transmitter] = sifted_key
        return sifted_key

    def mix_keys(self, key_1: str, key_2: str, new_key_name: str = ''):
        mixed_key = xor_bit_strings(key_1, key_2)
        if new_key_name != '':
            self.keys[new_key_name] = mixed_key
        return mixed_key

    def send_classical_bit_string(self, node_receiver: str, msg: str, key: str = ''):
        if key != '':
            assert len(key) == len(msg)
            msg = xor_bit_strings(msg, key)
        with CQCConnection(self.name) as Me:
            Me.sendClassical(
                        node_receiver,
                        encode_bit_string_to_bytes_msg(msg)
                    )

    def receive_classical_bit_string(self, length: str = default_key_length_required, key: str = ''):
        with CQCConnection(self.name) as Me:
            msg = Me.recvClassical()
            msg = decode_bytes_msg_to_bit_string(msg, length)
            if key != '':
                assert len(key) == len(msg)
                msg = xor_bit_strings(msg, key)
            return msg

    def send_classical_byte_string(self, node_receiver: str, msg: bytes, key: str = ''):
        if key != '':
            encoded_message = []
            for i in range(len(msg)):
                encoded_message.append(msg[i] ^ int(key[8*i:8*(i+1)], 2))
        else:
            encoded_message = msg
        with CQCConnection(self.name) as Me:
            Me.sendClassical(node_receiver, encoded_message)

    def receive_classical_byte_string(self, key: str = ''):
        with CQCConnection(self.name) as Me:
            msg = Me.recvClassical()
            if key != '':
                decoded_message = []
                for i in range(len(msg)):
                    decoded_message.append(msg[i] ^ int(key[8*i:8*(i+1)], 2))
            else:
                decoded_message = msg
            return decoded_message

    def send_classical_int_list(self, receiver: str, msg: list):
        """
        This function was made to avoid error when sending empty lists.
        :param receiver: Receiver node name.
        :param msg: List of integers each <= 255, the list length also <= 255.
        :return:
        """
        # TODO: Numbers more than 256
        with CQCConnection(self.name) as Me:
            # Later it's gonna be something like:
            # messages_amount = len(msg) // 255
            # print(f"{self.name} to {receiver}: {msg}")
            msg = [len(msg) // 256] + msg
            Me.sendClassical(receiver, msg)

    def receive_classical_int_list(self):
        """
        This function was made to avoid error when receiving empty lists.
        :return:
        """
        # TODO: Numbers more than 256
        with CQCConnection(self.name) as Me:
            msg = list(Me.recvClassical())
            msg = msg[1:]
        return msg
