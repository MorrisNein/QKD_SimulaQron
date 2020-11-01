import time
import random
from textwrap import dedent
from cqc.pythonLib import CQCConnection, qubit, CQCNoQubitError
from service import decode_bytes_msg_to_bit_string, encode_bit_string_to_bytes_msg,\
    key_length_required, key_message_length, xor_bit_strings


class Node(object):

    def __init__(self, name):
        self.name = name
        self.keys = {}

    def transmit_key(self, receiver):
        # Initialize the connection
        with CQCConnection(self.name) as Me:

            sifted_key = ''
            is_key_length_reached = False

            # Generate a raw_key_str in random basis
            for sifting_iteration in range(key_length_required // key_message_length * 3 + 3):

                raw_key_str = ''
                basis_str = ''

                for i in range(key_message_length):
                    raw_key_str += str(random.randint(0, 1))
                    basis_str += str(random.randint(0, 1))

                    # Create a qubit
                    q = qubit(Me)

                    # Encode the raw_key_str in the qubit
                    if int(raw_key_str[i]):
                        q.X()

                    # Choose the basis to send
                    if int(basis_str[i]):
                        q.H()

                    # Send qubit to Charlie
                    try:
                        Me.sendQubit(q, receiver)
                    except CQCNoQubitError:
                        time.sleep(0.2)
                        Me.sendQubit(q, receiver)

                print("====================================================\n"
                      "Sifting iteration {}\n".format(sifting_iteration))
                msg = Me.recvClassical()
                msg = decode_bytes_msg_to_bit_string(msg, key_message_length)

                print(dedent(
                    f"""
                                {self.name}'s key: {raw_key_str}
                                {self.name}'s basis: {basis_str}
                                {self.name} received {receiver}'s basis: {msg}
                                """))

                Me.sendClassical(receiver, encode_bit_string_to_bytes_msg(basis_str))

                for i in range(key_message_length):
                    if basis_str[i] == msg[i]:
                        sifted_key += raw_key_str[i]
                    if len(sifted_key) >= key_length_required:
                        is_key_length_reached = True
                        break
                if is_key_length_reached:
                    break

            print("{}'s sifted key: {}\n".format(self.name, sifted_key))
        self.keys[receiver] = sifted_key
        return sifted_key

    def receive_key(self, transmitter):
        with CQCConnection(self.name) as Me:

            sifted_key = ''
            is_key_length_reached = False

            # Generate a raw_key_str in random basis
            for sifting_iteration in range(key_length_required // key_message_length * 3 + 3):

                raw_key_str = ''
                basis_str = ''

                for i in range(key_message_length):
                    basis_str += str(random.randint(0, 1))

                    q = Me.recvQubit()

                    # Choose the basis to measure
                    if int(basis_str[i]):
                        q.H()

                    raw_key_str += str(q.measure())

                Me.sendClassical(transmitter, encode_bit_string_to_bytes_msg(basis_str))

                msg = Me.recvClassical()
                msg = decode_bytes_msg_to_bit_string(msg, key_message_length)
                print(dedent(
                    f"""
                    {self.name}'s key: {raw_key_str}
                    {self.name}'s basis: {basis_str}
                    {self.name} received {transmitter}'s basis: {msg}
                    """))

                for i in range(key_message_length):
                    if basis_str[i] == msg[i]:
                        sifted_key += raw_key_str[i]
                    if len(sifted_key) >= key_length_required:
                        is_key_length_reached = True
                        break
                if is_key_length_reached:
                    break

            print("{}'s sifted key: {}\n".format(self.name, sifted_key))
        self.keys[transmitter] = sifted_key
        return sifted_key

    def mix_keys(self, key_1, key_2, new_key_name):
        self.keys[new_key_name] = xor_bit_strings(key_1, key_2)

    def send_classical_bit_string(self, node_receiver, msg):
        with CQCConnection(self.name) as Me:
            Me.sendClassical(
                        node_receiver,
                        encode_bit_string_to_bytes_msg(msg)
                    )

    def receive_classical_bit_string(self, length=key_length_required):
        with CQCConnection(self.name) as Me:
            msg = Me.recvClassical()
            msg = decode_bytes_msg_to_bit_string(msg, length)
            return msg

        # def mix_and_publish_keys(self, node1: str, node2: str, public_key_receiver=None):
        #     if public_key_receiver is None:
        #         public_key_receiver = node2
        #
        #     with CQCConnection(self.name) as KeyPublisher:
        #         key_1 = self.keys[node1]
        #         key_2 = self.keys[node2]
        #         print(f"{node1}'s key: {key_1}")
        #         print(f"{node2}'s key: {key_2}")
        #         public_key = xor_bit_strings(key_1, key_2)
        #         print(f"{self.name} publishes key: {public_key} and sends it to {public_key_receiver}")
        #         KeyPublisher.sendClassical(
        #             public_key_receiver,
        #             encode_bit_string_to_bytes_msg(public_key)
        #         )
        #         return public_key
        #
        # def receive_and_mix_keys(self, key_decoder):
        #     with CQCConnection(self.name) as KeyReceiver:
        #         public_key = decode_bytes_msg_to_bit_string(KeyReceiver.recvClassical(), key_length_required)
        #         print('Public key', public_key)
        #         # raw_dk = bin(int(key_decoder, 2) ^ int(public_key, 2))[2:]
        #         print('-----decoder(bob-charlie) key', key_decoder)
        #         # decoded_key = '0' * (key_length_required - len(raw_dk)) + raw_dk
        #         decoded_key = xor_bit_strings()
        #         print('-----alices(?) key', decoded_key)
        #     return decoded_key
