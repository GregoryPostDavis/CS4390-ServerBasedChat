import hashlib
from Crypto.Cipher import AES


# FUNCTION FOR GENERATING CK_A
def cipher_key(rand, secret_key):
    hash_input = str(rand) + str(secret_key)

    ck_a = hashlib.md5(hash_input.encode())

    return ck_a.hexdigest()

# FUNCTION FOR ENCRYPTING MESSAGE
def encrypt_msg(ck_a, rand, tcp_port):
    cipher = AES.new(ck_a, AES.MODE_EAX) # CREATE AES CIPHER OBJECT
    ciphertext, tag = cipher.encrypt_and_digest(tcp_port) # ENCRYPTS MESSAGE

    data = ciphertext + tag

    return data

def decrypt_msg(message, ck_a):
    cipher = AES.new(ck_a, AES.MODE_EAX)
    cleartext = cipher.decrypt_and_verify(message)

    return cleartext
