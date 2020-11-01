import newNode
import service


def main():
    charlie = newNode.Node()
    charlie.initialize('Charlie')
    alice_key = charlie.receive_key('Alice')

    bob_key = charlie.receive_key('Bob')
    '''
    public_key = str(bin(int(alice_key, 2) ^ int(bob_key, 2))[2:])
    print('alice', alice_key)
    print('bob', bob_key)
    print('public', '0' * (service.key_length_required - len(public_key)) + public_key)
    decoded_alice = str(bin(int(bob_key, 2) ^ int(public_key, 2))[2:])
    print('decoded alice', '0' * (service.key_length_required - len(decoded_alice)) + decoded_alice)
    '''
    charlie.publish_key('Alice', 'Bob')


if __name__ == '__main__':
    main()
