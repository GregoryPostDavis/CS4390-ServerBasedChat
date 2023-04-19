import hashlib
import random

# FUNCTION FOR SERVER-SIDE AUTHENTICATION
def server_hash(secret_key):
    rand = random.randint(1000000000,9999999999) 
    #print(rand)                                        #- DEBUG

    hash_input = str(rand) + str(secret_key)
    #print("\nhash_input: %s" %(hash_input))            #- DEBUG

    xres = hashlib.sha256(hash_input.encode())          # A3 ALGORITHM
    #print("\nauthentication function: %s" %(xres.hexdigest())) #- DEBUG

    return str(rand), xres.hexdigest()

# FUNCTION FOR CLIENT-SIDE AUTHENTICATION
def client_hash(challenge, secret_key):
    #print(challenge)                                   #- DEBUG
    #print(secret_key)                                  #- DEBUG
    
    hash_input =  str(challenge) + str(secret_key)
    #print("\nhash_input: %s" %(hash_input))            #- DEBUG
   
    res = hashlib.sha256(hash_input.encode())           # A3 ALGORITHM
    #print("\nauthentication function: %s" %(res.hexdigest)) #- DEBUG

    return res.hexdigest()

# FUNCTION FOR CHECKING XRES AND RES
def check_hash(xres, res):
    if xres == res:                                     # AUTH SUCCESS
        return 1
    else:                                               # AUTH FAIL
        return 0
