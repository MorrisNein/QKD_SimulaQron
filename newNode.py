import time
import random
import service
from textwrap import dedent
from cqc.pythonLib import CQCConnection, qubit, CQCNoQubitError
from service import decode_bytes_msg_to_bitstring, encode_bitstring_to_bytes_msg,\
    key_length_required, key_message_length


class Node:

    name = ''
    sifted_keys = {}

    def initialize(self, name):
        self.name = name

    def transmit_key(self, neighbour):
        # Initialize the connection
        with CQCConnection(self.name) as Transmitter:

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
                    q = qubit(Transmitter)

                    # Encode the raw_key_str in the qubit
                    if int(raw_key_str[i]):
                        q.X()

                    # Choose the basis to send
                    if int(basis_str[i]):
                        q.H()

                    # Send qubit to Charlie
                    try:
                        Transmitter.sendQubit(q, neighbour)
                    except CQCNoQubitError:
                        time.sleep(0.2)
                        Transmitter.sendQubit(q, neighbour)

                msg = Transmitter.recvClassical()
                msg = decode_bytes_msg_to_bitstring(msg, key_message_length)
                print(dedent(
                    f"""
                                {self.name}'s key: {raw_key_str}
                                {self.name}'s basis: {basis_str}
                                {self.name} received {neighbour}'s basis: {msg}
                                """))
                Transmitter.sendClassical(neighbour, encode_bitstring_to_bytes_msg(basis_str))

                for i in range(key_message_length):
                    if basis_str[i] == msg[i]:
                        sifted_key += raw_key_str[i]
                    if len(sifted_key) >= key_length_required:
                        is_key_length_reached = True
                        break
                if is_key_length_reached:
                    break

            print("{}'s sifted key: {}\n".format(self.name, sifted_key))
        self.sifted_keys[neighbour] = sifted_key
        return sifted_key

    def receive_key(self, neighbour):
        with CQCConnection(self.name) as Receiver:

            sifted_key = ''
            is_key_length_reached = False

            # Generate a raw_key_str in random basis
            for sifting_iteration in range(key_length_required // key_message_length * 3 + 3):

                print("====================================================\n"
                      "Step {}\n".format(sifting_iteration))

                raw_key_str = ''
                basis_str = ''

                for i in range(key_message_length):
                    basis_str += str(random.randint(0, 1))

                    q = Receiver.recvQubit()

                    # Choose the basis to measure
                    if int(basis_str[i]):
                        q.H()

                    raw_key_str += str(q.measure())

                Receiver.sendClassical(neighbour, encode_bitstring_to_bytes_msg(basis_str))
                msg = Receiver.recvClassical()
                msg = decode_bytes_msg_to_bitstring(msg, key_message_length)
                print(dedent(
                    f"""
                    {self.name}'s key: {raw_key_str}
                    {self.name}'s basis: {basis_str}
                    {self.name} received {neighbour}'s basis: {msg}
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
        self.sifted_keys[neighbour] = sifted_key
        return sifted_key

    def publish_key(self, transmitter: str, receiver: str):
        with CQCConnection(transmitter) as Transmitter:
            key_to_transmit = self.sifted_keys[transmitter]
            encoder = self.sifted_keys[receiver]
            print('+++++key to encrypt(alice)', key_to_transmit)
            print('+++++encoder(bob-charlie)', encoder)
            raw_pk = bin(int(key_to_transmit, 2) ^ int(encoder, 2))[2:]
            public_key = '0' * (service.key_length_required - len(raw_pk)) + raw_pk
            print('++++charlie public key', public_key)
            Transmitter.sendClassical(receiver, encode_bitstring_to_bytes_msg(public_key))

    def decode_public_key(self, decoder):
        with CQCConnection(self.name) as Receiver:
            public_key = decode_bytes_msg_to_bitstring(Receiver.recvClassical(), service.key_length_required)
            print('-----public key', public_key)
            raw_dk = bin(int(decoder, 2) ^ int(public_key, 2))[2:]
            print('-----decoder(bob-charlie) key', decoder)
            decoded_key = '0' * (service.key_length_required - len(raw_dk)) + raw_dk
            print('-----alices(?) key', decoded_key)
        return decoded_key
