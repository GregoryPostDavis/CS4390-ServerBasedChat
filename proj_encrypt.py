import hashlib
#from Crypto.Cipher import AES # PRBLEM WITH LIBRARY & COMPATIBILITY. WILL NOT USE!


# FUNCTION FOR GENERATING CK_A
def cipher_key(rand, secret_key):
    hash_input = str(rand) + str(secret_key)

    ck_a = hashlib.md5(hash_input.encode())

    return ck_a.hexdigest()

# FUNCTION FOR ENCRYPTING MESSAGE
def encrypt_msg(ck_a, rand, tcp_port):
    cipher_key = ck_a                    # XOR ENCRYPTION KEY
    message = str(rand) + ";" + str(tcp_port) # PACK RAND_COOKIE AND PORT NUMBER INTO ONE MESSAGE
    length = len(message)

    
    for i in range(length):             # ENCRYPTS MESSAGE
        message = (message[:i] +
                   chr(ord(message[i]) ^ ord(cipher_key[i])) +
                       message[i + 1:]) 
        
    return message

   
# FUNCTION FOR DECRYPTING MESSAGE
def decrypt_msg(message , ck_a: str):
    cipher_key = ck_a                    # XOR ENCRYPTION KEY
    message = str(message, "utf-8")      # BYTE TYPE TO STRING TYPE CONVERSION
    length = len(message)


    for i in range(length):             # DECRYPTS MESSAGE
        message = (message[:i] +
                   chr(ord(message[i]) ^ ord(cipher_key[i])) +
                       message[i + 1:]) 
        
    return message
