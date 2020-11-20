if __name__ != "__main__":
    # Default bit length of generated key
    default_key_length_required = 16
    # Default bit length of portions of key generation. Currently must be no more than 255.
    default_key_message_length = 256
    # Default quantum channel gain
    default_g_q = 0.5

    def decode_bytes_msg_to_bit_string(s, length):
        s = bin(int(s.hex(), 16))[2:]
        s = "0" * (length - len(s)) + s
        return s

    def encode_bit_string_to_bytes_msg(bitstring):
        bitstring = "".join(bitstring.split())
        assert len(bitstring) % 8 == 0
        return [int(bitstring[i:i + 8], 2) for i in range(0, len(bitstring), 8)]

    def xor_bit_strings(str_1, str_2):
        assert len(str_1) == len(str_2)
        xor_str = bin(int(str_1, 2) ^ int(str_2, 2))[2:]
        xor_str = '0' * (len(str_1) - len(xor_str)) + xor_str
        return xor_str
