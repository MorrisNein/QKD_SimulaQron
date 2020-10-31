if __name__ != "__main__":
    key_length_required = 16
    # key_message_length must be 8 * n
    key_message_length = 8 * 1


    def decode_bytes_msg_to_bitstring(s, length):
        s = bin(int(s.hex(), 16))[2:]
        s = "0" * (length - len(s)) + s
        return s


    def encode_bitstring_to_bytes_msg(bitstring):
        bitstring = "".join(bitstring.split())
        assert len(bitstring) % 8 == 0
        return [int(bitstring[i:i + 8], 2) for i in range(0, len(bitstring), 8)]
