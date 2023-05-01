import hashlib
#from Crypto.Cipher import AES # PRBLEM WITH LIBRARY & COMPATIBILITY. WILL NOT USE!


# FUNCTION FOR GENERATING CK_A
def cipher_key(rand, secret_key):
    hash_input = str(rand) + str(secret_key)

    ck_a = hashlib.sha512(hash_input.encode()) # A8 ALGORITHM

    return ck_a.hexdigest()

# FUNCTION FOR ENCRYPTING AUTH_SUCCESS MESSAGE
def encrypt_authmsg(ck_a, rand, tcp_port):
    cipher_key = ck_a                    # XOR ENCRYPTION KEY
    message = str(rand) + ";" + str(tcp_port) # PACK RAND_COOKIE AND PORT NUMBER INTO ONE MESSAGE
    length = len(message)

    
    for i in range(length):             # ENCRYPTS MESSAGE
        message = (message[:i] +
                   chr(ord(message[i]) ^ ord(cipher_key[i])) +
                       message[i + 1:]) 
        
    return message

# FUNCTION FOR ENCRYPTING CHAT MESSAGES
def encrypt_msg(ck_a, msg):
    cipher_key = ck_a
    length = len(msg)
    
    for i in range(length):
        cipher_key_i = cipher_key[i % len(cipher_key)]      # HANDLES THE CASE WHERE THE LENGTH OF CK_A IS SHORTER THAN MSG BY TAKING THE MODULUS OF THE CURRENT INDEX WITH THE LENGTH OF CK_A
        msg = (msg[:i] +
                   chr(ord(msg[i]) ^ ord(cipher_key_i)) +
                       msg[i + 1:]) 

    #print(msg)                          #- DEBUG

    return msg

   
# FUNCTION FOR DECRYPTING MESSAGE
def decrypt_msg(message , ck_a):
    cipher_key = ck_a                    # XOR ENCRYPTION KEY

    if isinstance(message, bytes):       # IF MESSAGE IS BYTE TYPE
        message = str(message, "utf-8")  # BYTE TO STRING CONVERSION

    length = len(message)

    for i in range(length):              # DECRYPTS MESSAGE
        cipher_key_i = cipher_key[i % len(cipher_key)]      # HANDLES THE CASE WHERE THE LENGTH OF CK_A IS SHORTER THAN MSG BY TAKING THE MODULUS OF THE CURRENT INDEX WITH THE LENGTH OF CK_A
        message = (message[:i] +
                   chr(ord(message[i]) ^ ord(cipher_key_i)) +
                       message[i + 1:]) 
        
    return message