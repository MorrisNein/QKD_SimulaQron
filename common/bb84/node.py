import time
import random
import threading
from functools import wraps
import numpy as np
from textwrap import dedent
from cqc.pythonLib import CQCConnection, qubit, CQCNoQubitError
from common.bb84.service import *
from common.bb84.cascade import run_cascade, calculate_block_parity

mutex_cascade = threading.Lock()
mutex_send_classical_message = threading.Lock()
mutex_receive_classical_message = threading.Lock()

ask_parity_msg_count = 0
reveal_parity_msg_count = 0


def send_message_wrapper(func):
    @wraps(func)
    def wrapper_decorator(*args, **kwargs):
        # Do something before
        mutex_send_classical_message.acquire()

        value = func(*args, **kwargs)

        # Do something after
        mutex_send_classical_message.release()

        return value
    return wrapper_decorator


def receive_message_wrapper(func):
    @wraps(func)
    def wrapper_decorator(*args, **kwargs):
        # Do something before
        # mutex_receive_classical_message.acquire()

        try:
            value = func(*args, **kwargs)
        except:
            value = func(*args, **kwargs)

        # Do something after
        # mutex_receive_classical_message.release()

        return value
    return wrapper_decorator


class Node:

    def __init__(self, name):
        self.name = name
        self.keys = {}

    def __del__(self):
        print(f"{self.name} node closed.")

    # ================ QKD ================

    def transmit_key(self, receiver: str, key_length_required: int = default_key_length_required,
                     g_q: int = default_g_q, delta: float = default_delta, logging_level: int = 1,
                     qber: float = default_qber):
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
        :param delta:
            Probability of choosing basis "0" for encoding. Default value is 0.5.
            Usually the same as receiver has.
        :param qber:
            Probability of quantum bit-flip.
        :return:
        """

        key_message_length = default_key_message_length
        sifting_iterations_limit = int(key_length_required / key_message_length / g_q * 3 + 3)

        # assert self.receive_classical_string() == f"{receiver} start".encode()

        # Initialize the connection
        with CQCConnection(self.name) as Me:
            correct_key = ''
            is_key_length_reached = False

            # Generate a raw_key_str in random basis
            for sifting_iteration in range(sifting_iterations_limit):
                raw_key_str = ''
                bases_str = ''

                for pos_num in range(key_message_length):
                    # ================= Raw key message =================
                    # Create a qubit in a current node
                    q = qubit(Me)  # CQC

                    # Encode the qubit by random number
                    raw_key_str += str(random.randint(0, 1))
                    if int(raw_key_str[pos_num]):
                        q.X()

                    # Choose random basis to send
                    if delta <= random.random():
                        bases_str += '1'
                        q.H()
                    else:
                        bases_str += '0'

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
                received_key_positions_o = list(self.receive_classical_int_list(key_message_length))  # CQC2
                # ... and keep only the same positions of key and basis
                raw_key_str = ''.join([raw_key_str[pos] for pos in received_key_positions_o])
                bases_str = ''.join([bases_str[pos] for pos in received_key_positions_o])

                # ================= Sifting messages =================
                # Get other node's positions of changed basis
                bases_str_o = self.receive_classical_bit_string(len(received_key_positions_o))  # CQC3
                # Send the changed basis positions
                self.send_classical_bit_string(receiver, bases_str)  # CQC4

                # ================= Logging =================
                if logging_level >= 2:
                    print(dedent(
                        f"""	
                        {self.name}'s key: {raw_key_str}	
                        {self.name}'s bases: {bases_str}	
                        {self.name} received {receiver}'s bases: {bases_str_o}	
                        {self.name} knows that key positions received by {receiver} are: {received_key_positions_o}	
                        """))

                # ================= Sifting =================
                same_bases_number = 0
                for pos_num, _ in enumerate(received_key_positions_o):
                    if bases_str[pos_num] == bases_str_o[pos_num]:
                        correct_key += raw_key_str[pos_num]
                        same_bases_number += 1

                    # ================= Sifting iteration break check =================
                    if len(correct_key) >= key_length_required:
                        is_key_length_reached = True
                        break

                # ================= Protocol gain metric =================
                # (pos_num + 1) value now contains number of key positions checked before break
                g_p_iter = same_bases_number / (pos_num + 1)
                if sifting_iteration == 0:
                    g_p = g_p_iter
                else:
                    g_p = (g_p + g_p_iter) / 2

                # ================= Sifting iteration break check =================
                if is_key_length_reached:
                    break
            else:
                print("Iterations limit expired!")

            # ================= Sifted key report =================
            if logging_level >= 2:
                print(f"{self.name}'s sifted key to {receiver}: {correct_key}\n"
                      f"Empirical protocol gain is {round(g_p, 2)} with delta {delta}\n")

        # ================= Receiver's key adjustment =================
        self.correct_key_errors_as_transmitter(receiver, correct_key, qber)

        # ================= Correct key report =================
        if logging_level >= 2:
            print(f"{self.name}'s correct key to {receiver}: {correct_key}\n"
                  f"Empirical protocol gain is {round(g_p, 2)} with delta {delta}\n")

        # ================= The end =================
        self.keys[receiver] = correct_key
        return correct_key

    def receive_key(self, transmitter: str, key_length_required: int = default_key_length_required,
                    g_q: int = default_g_q, delta: float = default_delta, logging_level: int = 1,
                    qber: float = default_qber):
        """
        Receiver part of quantum key distribution.
        The transmitter node must run function transmit_key simultaneously.

        :param transmitter:
            Name of the transmitter node specified in the network topology.
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
        :param delta:
            Probability of choosing basis "0" for decoding. Default value is 0.5.
            Usually the same as transmitter has.
        :param qber:
            Probability of quantum bit-flip.
        :return:
        """

        key_message_length = default_key_message_length
        sifting_iterations_limit = int(key_length_required / key_message_length / g_q * 3 + 3)

        # self.send_classical_string(transmitter, f"{self.name} start".encode())

        with CQCConnection(self.name) as Me:

            sifted_key = ''
            is_key_length_reached = False

            # Generate a raw_key_str in random basis
            for sifting_iteration in range(sifting_iterations_limit):

                raw_key_str = ''
                bases_str = ''
                received_key_positions = []

                for i in range(key_message_length):
                    # ================= Raw key message =================
                    q = Me.recvQubit()  # CQC1

                    # ================= Loss by quantum channel gain  =================
                    # Here we insert the loss by quantum channel gain < 1.
                    # If g_q is less or equal than a random uniform number [0,1],
                    # then the next iteration is being started.
                    if g_q <= random.random():
                        q.release()
                        continue  # the qubit is lost, proceed to the next one
                    # ==================================

                    # Remember current position to notify transmitter that it was received properly
                    received_key_positions += [i]

                    # Choose random basis to measure the received qubit
                    if delta <= random.random():
                        bases_str += '1'
                        q.H()
                    else:
                        bases_str += '0'
                    # ================= Error by QBER  =================
                    # Here we insert the bif-flip errors by qber > 0.
                    if random.random() <= qber:
                        q.X()
                    # ==================================

                    raw_key_str += str(q.measure())

                # ================= Raw key adjustment =================
                self.send_classical_int_list(transmitter, received_key_positions)  # CQC2

                # ================= Sifting messages =================
                # Send the node's positions of changed basis
                self.send_classical_bit_string(transmitter, bases_str)  # CQC3
                # Get other node's positions of changed basis
                bases_str_o = self.receive_classical_bit_string(len(received_key_positions))  # CQC4

                # ================= Logging =================
                if logging_level >= 2:
                    print(dedent(
                        f"""
                        {self.name}'s key: {raw_key_str}
                        {self.name}'s bases: {bases_str}
                        {self.name} received {transmitter}'s bases: {bases_str_o}
                        """))

                # ================= Sifting =================
                for pos_num, _ in enumerate(received_key_positions):
                    if bases_str[pos_num] == bases_str_o[pos_num]:
                        sifted_key += raw_key_str[pos_num]

                    # ================= Break check =================
                    if len(sifted_key) >= key_length_required:
                        is_key_length_reached = True
                        break
                if is_key_length_reached:
                    break
            else:
                print("Iterations limit expired!")

            # ================= Sifted key report =================
            if logging_level >= 2:
                print(f"{self.name}'s sifted key to {transmitter}: {sifted_key}")

        # ================= Receiver's key adjustment =================
        correct_key = self.correct_key_errors_as_receiver(transmitter, sifted_key, qber)
        # ================= Correct key report =================
        if logging_level >= 1:
            print(f"{self.name}'s correct key to {transmitter}: {correct_key}")

        # ================= The end =================
        self.keys[transmitter] = correct_key
        return correct_key

    def mix_keys(self, key_1: str, key_2: str, new_key_name: str = ''):
        mixed_key = xor_bit_strings(key_1, key_2)
        if new_key_name != '':
            self.keys[new_key_name] = mixed_key
        return mixed_key

    # ================ errors correction ================

    def correct_key_errors_as_receiver(self, transmitter, initial_key, qber):
        if qber == 0:
            return

        mutex_cascade.acquire()
        corrected_key = run_cascade(lambda k_p: self.ask_block_parity(transmitter, k_p),
                                    initial_key,
                                    qber)
        mutex_cascade.release()

        self.send_classical_int_list(transmitter, [])

        return corrected_key

    def ask_block_parity(self, node_partner_name, key_block_positions):
        global ask_parity_msg_count
        ask_parity_msg_count += 1
        # print(f"{self.name} asks parity_msg_num {ask_parity_msg_num}")
        self.send_classical_int_list(node_partner_name, key_block_positions)
        return self.receive_classical_int_list(1)[0]

    def correct_key_errors_as_transmitter(self, node_partner_name, correct_key, qber):
        t1 = time.time()

        if qber == 0:
            return
        keep_answering = True
        while keep_answering:
            keep_answering = self.reveal_block_parity(node_partner_name, correct_key)
        t2 = time.time()
        print(f"CASCADE run {round(t2 - t1, 2)} s")

    def reveal_block_parity(self, node_partner_name, correct_key):
        global reveal_parity_msg_count
        reveal_parity_msg_count += 1
        msg = self.receive_classical_int_list(list_max_length=len(correct_key))
        if not msg:
            return False

        key_block_positions = msg
        parity = calculate_block_parity(correct_key, key_block_positions)
        # print(f"{self.name} answers parity_msg_num {reveal_parity_msg_num}")
        self.send_classical_int_list(node_partner_name, [parity])

        return True

    # ================ classic messages exchange ================

    @send_message_wrapper
    def send_classical_bit_string(self, receiver: str, msg: str, key: str = ''):
        """
        Function for sending compact bit-strings.
        :param receiver:
            Receiver node name specified in the network topology.
        :param msg:
            String consisting of 0 and 1.
        :param key:
            Bit-string key for encoding via XOR. Must be equal to len(msg)
        :return:
        """
        msg_len = len(msg)

        if key != '':
            assert len(key) == msg_len
            msg = xor_bit_strings(msg, key)

        if msg_len is not None:
            # Converting the string to natural number of bytes
            msg = '0'*((8 - (msg_len % 8)) % 8) + msg

        with CQCConnection(self.name) as Me:
            if msg_len != 0:
                Me.sendClassical(
                    receiver,
                    encode_bit_string_to_bytes_msg(msg)
                )
            else:
                Me.sendClassical(
                    receiver,
                    "empty_string".encode("utf-8")
                )

    @receive_message_wrapper
    def receive_classical_bit_string(self, msg_len: int = None, key: str = ''):
        """
        Function for receiving compact bit-strings.
        :param msg_len:
            Length of string. Must be specified if (msg_len % 8) != 0.
            The receiver must also know the length in this case.
        :param key:
            Bit-string key for encoding via XOR. Must be equal to len(msg)
        :return:
        """
        with CQCConnection(self.name) as Me:
            msg = Me.recvClassical()
            msg_bytes = len(msg)

            if msg == "empty_string".encode("utf-8"):
                return ""

            if msg_len is None:
                msg_len = msg_bytes * 8

            msg = decode_bytes_msg_to_bit_string(msg, msg_len)

            if key != '':
                assert len(key) == len(msg)
                msg = xor_bit_strings(msg, key)
            return msg

    @send_message_wrapper
    def send_classical_string(self, receiver: str, msg: bytes, key: str = ''):
        if key != '':
            encoded_message = []
            for i in range(len(msg)):
                encoded_message.append(msg[i] ^ int(key[8 * i:8 * (i + 1)], 2))
        else:
            encoded_message = msg
        with CQCConnection(self.name) as Me:
            Me.sendClassical(receiver, encoded_message)

    @receive_message_wrapper
    def receive_classical_string(self, key: str = ''):
        with CQCConnection(self.name) as Me:
            msg = Me.recvClassical()
            if key != '':
                decoded_message = []
                for i in range(len(msg)):
                    decoded_message.append(msg[i] ^ int(key[8 * i:8 * (i + 1)], 2))
            else:
                decoded_message = msg
            return decoded_message

    @send_message_wrapper
    def send_classical_int_list(self, receiver: str, msg: list):
        """
        This function was made to avoid error when sending empty lists
        or integers >256.
        :param receiver:
            Receiver node name specified in the network topology.
        :param msg:
            List of integers each <= 2**16.
        :return:
        """
        msg = np.array(msg)
        # The reason is limitation of sendClassical method
        # True when the initial list contains numbers large than 256
        is_factors_list_needed = sum(msg // 256) > 0

        if is_factors_list_needed:
            factors_of_256 = msg // 256
            remainders = msg % 256
            msg = np.append(factors_of_256, remainders)

        # The first byte of the message is 'info' byte
        msg = np.append(int(is_factors_list_needed), msg)
        msg = msg.astype(int)  # if msg is empty, previous step results in array([0.0])
        msg = msg.tolist()

        # If the message does not start with 0, it must contain odd num of bytes
        assert not (msg[0] != 0 and len(msg) % 2 == 0)

        with CQCConnection(self.name) as Me:
            Me.sendClassical(receiver, msg)

    @receive_message_wrapper
    def receive_classical_int_list(self, list_max_length: int):
        """
        This function was made to avoid error when receiving empty lists
        or integers >256.
        :param list_max_length: The expected maximum length or received list.
        :return:
        """
        # We receive a message with L = 2l+1 (bytes) that contains:
        # 1 info byte,
        # list of factors of 256 of length l
        # list of remainders of length l
        message_max_length = 1 + list_max_length * 2
        with CQCConnection(self.name) as Me:
            msg = list(Me.recvClassical(msg_size=message_max_length))
            # If the message does not start with 0, it must contain odd num of bytes
            assert not (msg[0] != 0 and len(msg) % 2 == 0)
            # The first info byte denotes if we need factors of 256
            # It also has a potential to signal whether we need to use sign, etc.
            is_factors_list_needed = msg[0]
            # We don't need it after the information is extracted
            msg = msg[1:]

        # Getting initial numbers
        if bool(is_factors_list_needed):
            msg = np.array(msg)

            msg_len_2 = len(msg) // 2

            factors_of_256 = msg[:msg_len_2]
            remainders = msg[msg_len_2:]

            msg = remainders + 256 * factors_of_256
            msg = msg.tolist()

        return msg
