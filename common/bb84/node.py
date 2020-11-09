import time
import random
from textwrap import dedent
from cqc.pythonLib import CQCConnection, qubit, CQCNoQubitError
from common.bb84.service import decode_bytes_msg_to_bit_string, encode_bit_string_to_bytes_msg,\
    default_key_length_required, key_message_length, xor_bit_strings


class Node(object):

    def __init__(self, name):
        self.name = name
        self.keys = {}

    def transmit_key(self, receiver: str, key_length_required: int = default_key_length_required, logging_level: int = 1):
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

                if logging_level >= 2:
                    print("====================================================\n"
                          "Sifting iteration {}\n".format(sifting_iteration))
                msg = Me.recvClassical()
                msg = decode_bytes_msg_to_bit_string(msg, key_message_length)

                if logging_level >= 2:
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

            if logging_level >= 1:
                print(f"{self.name}'s sifted key to {receiver}: {sifted_key}")

        self.keys[receiver] = sifted_key
        return sifted_key

    def receive_key(self, transmitter: str, key_length_required: int = default_key_length_required, logging_level: int = 1):
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
                if logging_level >= 2:
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

    def send_classical_int(self, node: str, msg: int):
        with CQCConnection(self.name) as Me:
            Me.sendClassical(node, msg)

    def receive_classical_int(self, node: str):
        with CQCConnection(self.name) as Me:
            msg = Me.recvClassical(node)
        return msg
