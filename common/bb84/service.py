if __name__ != "__main__":
    # Default bit length of generated key. Must be 8*n
    default_key_length_required = 256
    # Default bit length of portions of key generation. Currently must be no more than 2**16.
    default_key_message_length = 1024
    # Default quantum channel gain
    default_g_q = 0.25
    # Default delta. The probability of changing basis of transmission.
    # Defines protocol gain g_p as follows: g_p = delta**2 - 2*delta + 1
    default_delta = 0.5
    # QBER of the channel. The probability of bit-flip. QBER stands for quantum bit error rate
    default_qber = 0.15

    def decode_bytes_msg_to_bit_string(s, length):
        s = bin(int(s.hex(), 16))[2:]
        s = "0" * (length - len(s)) + s
        return s

    def encode_bit_string_to_bytes_msg(bitstring):
        bitstring = "".join(bitstring.split())
        # assert len(bitstring) % 8 == 0
        return [int(bitstring[i:i + 8], 2) for i in range(0, len(bitstring), 8)]

    def xor_bit_strings(str_1, str_2):
        assert len(str_1) == len(str_2)
        xor_str = bin(int(str_1, 2) ^ int(str_2, 2))[2:]
        xor_str = '0' * (len(str_1) - len(xor_str)) + xor_str
        return xor_str
