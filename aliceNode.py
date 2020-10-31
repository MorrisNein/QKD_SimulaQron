import time
import random
from textwrap import dedent

from cqc.pythonLib import CQCConnection, qubit, CQCNoQubitError

from service import decode_bytes_msg_to_bitstring, encode_bitstring_to_bytes_msg,\
    key_length_required, key_message_length


def main():
    # Initialize the connection
    with CQCConnection("Alice") as Alice:

        sifted_key = ''
        # key_length_required = 16
        # max value is 8
        # key_message_length = 8 * 3
        is_key_length_reached = False

        # Generate a raw_key_str in random basis
        for sifting_iteration in range(key_length_required // key_message_length * 3 + 3):

            # print("Step {}\n".format(sifting_iteration))

            raw_key_str = ''
            basis_str = ''

            for i in range(key_message_length):
                raw_key_str += str(random.randint(0, 1))
                basis_str += str(random.randint(0, 1))

                # Create a qubit
                q = qubit(Alice)

                # Encode the raw_key_str in the qubit
                if int(raw_key_str[i]):
                    q.X()

                # Choose the basis to send
                if int(basis_str[i]):
                    q.H()

                # Send qubit to Charlie
                try:
                    Alice.sendQubit(q, "Charlie")
                except CQCNoQubitError:
                    time.sleep(0.2)
                    Alice.sendQubit(q, "Charlie")

                # # Encode and send a classical message m to Bob
                # m = 0
                # enc = (m + k) % 2
                # Alice.sendClassical("Bob", enc)

                # print("Alice send the message m={} to Bob".format(m))

            # print("Alice's key: {}".format(raw_key_str))
            # print("Alice's basis: {}".format(basis_str))

            msg = Alice.recvClassical()
            msg = decode_bytes_msg_to_bitstring(msg, key_message_length)
            # print("Alice received Charlie's basis: {}".format(msg))
            print(dedent(
                        f"""
                        Alice's key: {raw_key_str}
                        Alice's basis: {basis_str}
                        Alice received Charlie's basis: {msg}
                        """))
            Alice.sendClassical("Charlie", encode_bitstring_to_bytes_msg(basis_str))

            for i in range(key_message_length):
                if basis_str[i] == msg[i]:
                    sifted_key += raw_key_str[i]
                if len(sifted_key) >= key_length_required:
                    is_key_length_reached = True
                    break
            if is_key_length_reached:
                break

        print("Alice's sifted key: {}\n".format(sifted_key))


if __name__ == '__main__':
    main()
