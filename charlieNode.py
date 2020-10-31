import random
from textwrap import dedent

from cqc.pythonLib import CQCConnection

from service import decode_bytes_msg_to_bitstring, encode_bitstring_to_bytes_msg,\
    key_length_required, key_message_length


def main():
    # Initialize the connection
    with CQCConnection("Charlie") as Charlie:

        sifted_key = ''
        # key_length_required = 16
        # max value is 8
        # key_message_length = 8 * 3
        is_key_length_reached = False

        # Generate a raw_key_str in random basis
        for sifting_iteration in range(key_length_required // key_message_length * 3 + 3):

            print("\nStep {}\n".format(sifting_iteration))

            raw_key_str = ''
            basis_str = ''

            for i in range(key_message_length):
                basis_str += str(random.randint(0, 1))

                q = Charlie.recvQubit()

                # Choose the basis to measure
                if int(basis_str[i]):
                    q.H()

                raw_key_str += str(q.measure())

            # print("Charlie's key: {}".format(raw_key_str))
            # print("Charlie's basis: {}".format(basis_str))

            Charlie.sendClassical("Alice", encode_bitstring_to_bytes_msg(basis_str))
            msg = Charlie.recvClassical()
            msg = decode_bytes_msg_to_bitstring(msg, key_message_length)
            # print("Charlie received Alice's basis: {}".format(msg))
            print(dedent(
                f"""
                Charlie's key: {raw_key_str}
                Charlie's basis: {basis_str}
                Charlie received Alice's basis: {msg}
                """))


            for i in range(key_message_length):
                if basis_str[i] == msg[i]:
                    sifted_key += raw_key_str[i]
                if len(sifted_key) >= key_length_required:
                    is_key_length_reached = True
                    break
            if is_key_length_reached:
                break

        print("\nCharlie's sifted key: {}".format(sifted_key))


if __name__ == '__main__':
    main()
