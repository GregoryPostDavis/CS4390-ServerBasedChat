import socket
import struct
import proj_auth
import proj_encrypt

def udpsend(udp_socket, client_address, message):
    udp_socket.sendto(message.encode(), client_address)
    print("You: " + message) # debug

def udpreceive(udp_socket):
    message, client_address = udp_socket.recvfrom(1024) # receive HELLO message
    message = message.decode()
    print("Client: " + message)
    return message, client_address

def tcpsend(client_socket, message):
    print("You: " + message)
    client_socket.send(message.encode('utf-8')) # TODO: the encoding will be replaced with CK-A

def tcpreceive(client_socket):
    message = client_socket.recv(1024).decode()
    print("Client: " + message) # buffer size not that important, if it goes over it will be saved
    return message

#####################################################

# predefined values
subscriber_list = [('clientA', 100),('clientB', 200),('clientC', 300)] # predefined subscriber list
subscriber_search = dict(subscriber_list)

IP = '127.0.0.1'
UDP_PORT = 1234

# UDP socket creation
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # AF_INET: internet, SOCK_DGRAM: UDP
udp_socket.bind((IP, UDP_PORT))
print("\n* UDP socket bound to %s" %(UDP_PORT))  # debug
print("* Waiting for client response...\n")  # debug

# HELLO
message, client_address = udpreceive(udp_socket)
client_id = message[6:-1]  # extract the client ID

# Verification
if client_id in subscriber_search:
    udpsend(udp_socket, client_address, f"Hello, {client_id}! Welcome to the server!")

    # TODO: authentication
    #   DONE - retrieve the client's secret key 
    #   DONE - send CHALLENGE message
    #   DONE - receive RESPONSE
    #   - if failure: send AUTH-FAIL message
    #   - if success: generate encryption key CK-A and send AUTH-SUCCESS encrypted in that key
    
    challenge_message, xres = proj_auth.server_hash(subscriber_search['clientA'])

    udpsend(udp_socket, client_address, challenge_message) # SENDS CHALLENGE(RAND) MESSAGE TO CLIENT
    #print("server xres: %s" %(xres)) - DEBUG

    message, client_address = udpreceive(udp_socket) # RECEIVES RESPONSE(RES) FROM CLIENT
    res = message
    
    # CHECKS XRES AND RES
    if proj_auth.check_hash(xres, res): 
        ck_a = proj_encrypt.cipher_key(challenge_message, subscriber_search['clientA'])
        data = proj_encrypt.encrypt_msg(ck_a, challenge_message, 5675)
        print("\nCK_A: %s" %(ck_a))
        udpsend(udp_socket, client_address, f"{client_id} AUTH_SUCCESS")
        udpsend(udp_socket, client_address, data)
    else:
        udpsend(udp_socket, client_address, f"{client_id} AUTH_FAIL")

    # TCP Socket
    TCP_PORT = 5678
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # #AF_INET: internet, SOCK_STREAM: TCP
    tcp_socket.bind((IP, TCP_PORT))
    tcp_socket.listen()

    client_socket, address = tcp_socket.accept() # Returns client socket and address
    print("\n* TCP socket bound to %s" %(TCP_PORT))

    tcpreceive(client_socket)
    tcpsend(client_socket, "Hello Client!")

    # TODO: connection
        #   - receive CONNECT, send CONNECTED

else:
    print("Client is not in the subscriber list.")

udp_socket.close()