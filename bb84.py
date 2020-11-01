# import time
# import random
# from textwrap import dedent
#
# from cqc.pythonLib import CQCConnection, qubit, CQCNoQubitError
#
# from service import decode_bytes_msg_to_bit_string, encode_bit_string_to_bytes_msg,\
#     key_length_required, key_message_length
#
#
# def transmit_key(name: str, recipient: str):
#     # Initialize the connection
#     with CQCConnection(name) as Transmitter:
#
#         sifted_key = ''
#         is_key_length_reached = False
#
#         # Generate a raw_key_str in random basis
#         for sifting_iteration in range(key_length_required // key_message_length * 3 + 3):
#
#             raw_key_str = ''
#             basis_str = ''
#
#             for i in range(key_message_length):
#                 raw_key_str += str(random.randint(0, 1))
#                 basis_str += str(random.randint(0, 1))
#
#                 # Create a qubit
#                 q = qubit(Transmitter)
#
#                 # Encode the raw_key_str in the qubit
#                 if int(raw_key_str[i]):
#                     q.X()
#
#                 # Choose the basis to send
#                 if int(basis_str[i]):
#                     q.H()
#
#                 # Send qubit to Charlie
#                 try:
#                     Transmitter.sendQubit(q, recipient)
#                 except CQCNoQubitError:
#                     time.sleep(0.2)
#                     Transmitter.sendQubit(q, recipient)
#
#             msg = Transmitter.recvClassical()
#             msg = decode_bytes_msg_to_bit_string(msg, key_message_length)
#             print(dedent(
#                         f"""
#                         {name}'s key: {raw_key_str}
#                         {name}'s basis: {basis_str}
#                         {name} received {recipient}'s basis: {msg}
#                         """))
#             Transmitter.sendClassical(recipient, encode_bit_string_to_bytes_msg(basis_str))
#
#             for i in range(key_message_length):
#                 if basis_str[i] == msg[i]:
#                     sifted_key += raw_key_str[i]
#                 if len(sifted_key) >= key_length_required:
#                     is_key_length_reached = True
#                     break
#             if is_key_length_reached:
#                 break
#
#         print("{}'s sifted key: {}\n".format(name, sifted_key))
#     return sifted_key
#
#
# def receive_key(name: str, recipient: str):
#     with CQCConnection(name) as Receiver:
#
#         sifted_key = ''
#         is_key_length_reached = False
#
#         # Generate a raw_key_str in random basis
#         for sifting_iteration in range(key_length_required // key_message_length * 3 + 3):
#
#             print("====================================================\n"
#                   "Step {}\n".format(sifting_iteration))
#
#             raw_key_str = ''
#             basis_str = ''
#
#             for i in range(key_message_length):
#                 basis_str += str(random.randint(0, 1))
#
#                 q = Receiver.recvQubit()
#
#                 # Choose the basis to measure
#                 if int(basis_str[i]):
#                     q.H()
#
#                 raw_key_str += str(q.measure())
#
#             Receiver.sendClassical(recipient, encode_bit_string_to_bytes_msg(basis_str))
#             msg = Receiver.recvClassical()
#             msg = decode_bytes_msg_to_bit_string(msg, key_message_length)
#             print(dedent(
#                 f"""
#                 {name}'s key: {raw_key_str}
#                 {name}'s basis: {basis_str}
#                 {name} received {recipient}'s basis: {msg}
#                 """))
#
#             for i in range(key_message_length):
#                 if basis_str[i] == msg[i]:
#                     sifted_key += raw_key_str[i]
#                 if len(sifted_key) >= key_length_required:
#                     is_key_length_reached = True
#                     break
#             if is_key_length_reached:
#                 break
#
#         print("{}'s sifted key: {}\n".format(name, sifted_key))
#     return sifted_key
