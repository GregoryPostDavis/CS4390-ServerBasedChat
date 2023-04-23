import socket
import authentication
import encryption

def udpsend(udp_socket, server_address, message):
    udp_socket.sendto(message.encode(), server_address)
    print("You: " + message)

def udpreceive(udp_socket):
    response, server_address = udp_socket.recvfrom(1024) # server response
    print("Server: " + response.decode())
    return response, server_address

def tcpsend(tcp_socket, message, ck_a):
    tcp_socket.send(encryption.encrypt_msg(ck_a, message).encode())

def tcpreceive(tcp_socket):
    message, server_address = tcp_socket.recvfrom(1024)
    message = encryption.decrypt_msg(message.decode(), ck_a)
    print("Server: ", message)
    return message, server_address

#####################################################

# predefine values
client_id = 'clientA'  # hardcoded client ID: has to be in subscribed users list
secret_key = 100

# UDP socket creation
IP = '127.0.0.1'
UDP_PORT = 1234

server_address = (IP, UDP_PORT)
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("\n* UDP socket created\n")

# Log on
udpsend(udp_socket, server_address, f"HELLO({client_id})") # Protocol: send HELLO(client_ID)

# Authentication
response, server_address = udpreceive(udp_socket) # Protocol: receive CHALLENGE(rand)
challenge_message = response.decode()
challenge_message = challenge_message[10:-1] # Extract rand

res = authentication.client_hash(challenge_message, secret_key)
udpsend(udp_socket, server_address, f"RESPONSE({client_id}, {res})") # Protocol: send RESPONSE(res)

ck_a = encryption.cipher_key(challenge_message, secret_key)
#print("\nCK_A: %s" %(ck_a))                                    # - DEBUG

response, server_address = udp_socket.recvfrom(1024)
response = encryption.decrypt_msg(response.decode(), ck_a)
print("Server: " + response) # Protocol: receive AUTH_SUCCESS(rand_cookie, port_number)

RAND_COOKIE = response[13:-7] # Extract cookie
TCP_PORT = int(response[-5:-1]) # Extract tcp port number

#print("\nRand_Cookie: ", RAND_COOKIE)                           # - DEBUG
#print("TCP Port Numer: ", TCP_PORT)                         # - DEBUG
 
# TCP Socket establishment
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.connect((IP, TCP_PORT))
print("\n* TCP socket created\n")                               # - DEBUG

tcpsend(tcp_socket, f"CONNECT({RAND_COOKIE})", ck_a) # Protocol: send CONNECT(rand_cookie)
tcpreceive(tcp_socket) # Protocol: receive CONNECTED

# Send messages
while True:
    msg = input("You: ")
    tcpsend(tcp_socket, msg, ck_a) 
    if msg.strip().lower() == "log off":
        print("Logging off...\n")
        break

tcp_socket.close()
print("* TCP connection closed.")
udp_socket.close()
print("* UDP connection closed.")