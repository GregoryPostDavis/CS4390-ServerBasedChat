import socket
import authentication
import encryption
from _thread import *
import queue

def udpsend(udp_socket, client_address, message):
    udp_socket.sendto(message.encode(), client_address)
    print("You: " + message)

def udpreceive(udp_socket):
    message, client_address = udp_socket.recvfrom(1024)
    message = message.decode()
    print("Client: " + message)
    return message, client_address

def tcpsend(tcp_socket, message, ck_a):
    print("You: " + message)
    tcp_socket.send(encryption.encrypt_msg(ck_a, message).encode())

def tcpreceive(client_socket, client_id, ck_a):
    message = encryption.decrypt_msg(client_socket.recv(1024).decode(), ck_a)
    print(f"{client_id}: " + message)
    return message

def createClientConnection(c_id, c_addr):
    # TCP Socket
    TCP_PORT = subscriber_search.get(c_id,None)[1]
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((IP, TCP_PORT))
    tcp_socket.listen()

    client_socket, address = tcp_socket.accept() # Returns client socket and address
    print("\n* TCP socket bound to %s\n" % (TCP_PORT))

#####################################################


# predefined subscribers
subscriber_list = [('clientA', (100,4000,4100)),('clientB', (200,4010,4110)),('clientC', (300,4020,4120))]  # (ID, (Secret Key, Snd Port, Rec Port))
subscriber_search = dict(subscriber_list)
connection_list = []
connection_search = dict(connection_list)

# UDP socket creation
IP = '127.0.0.1'
UDP_PORT = 1234

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((IP, UDP_PORT))
print("\n* UDP socket bound to %s" %(UDP_PORT))
print("* Waiting for client response...\n")

# Client log on
message, client_address = udpreceive(udp_socket) # Protocol: receive HELLO(client_ID)
client_id = message[6:-1]  # extract the client ID

# Verification
if client_id in subscriber_search:
    # Authentication
    RAND_COOKIE, xres = authentication.server_hash(subscriber_search['clientA'])
    udpsend(udp_socket, client_address, f"CHALLENGE({RAND_COOKIE})") # Protocol: send CHALLENGE(rand)

    message, client_address = udpreceive(udp_socket) # Protocol: receives RESPONSE(client_ID, res)
    res = message[18:-1]
    
    # Checking xres and res
    if authentication.check_hash(xres, res):
        TCP_PORT = 5678 # temporary port allocation
        REC_PORT = 4545 # temporary listening port allocation
        # Encryption
        ck_a = encryption.cipher_key(RAND_COOKIE, subscriber_search['clientA'])
        message = f"AUTH_SUCCESS({RAND_COOKIE}, {TCP_PORT}, {REC_PORT})"
        print("You: " + message)
        udp_socket.sendto(encryption.encrypt_msg(ck_a, message).encode(), client_address) # Protocol: send AUTH_SUCCESS(rand_cookie, port_number)
    else:
        udpsend(udp_socket, client_address, "AUTH_FAIL")

    # TCP connection
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((IP, TCP_PORT))
    tcp_socket.listen()
    client_socket, address = tcp_socket.accept() # Returns client socket and address
    print("\n* TCP socket bound to %s\n" %(TCP_PORT))

    message = tcpreceive(client_socket, client_id, ck_a) # Protocol: receive CONNECT(rand_cookie)
    if str(RAND_COOKIE) == message[8:-1]: # Protocol: send CONNECTED
        tcpsend(client_socket, "CONNECTED\n", ck_a)

    # Receive messages
    while True:
        msg = tcpreceive(client_socket, client_id, ck_a)
        if msg.strip().lower() == "log off":
            print("logging off...\n")
            break
        
    client_socket.close()
    tcp_socket.close()
    print("* TCP connection closed.")
else:
    print("* Client is not in the subscriber list.")

udp_socket.close()
print("* UDP connection closed.")