import socket
import time

def udpsend(udp_socket, server_address, message):
    udp_socket.sendto(message.encode(), server_address)
    print("You: " + message)

def udpreceive(udp_socket):
    response, server_address = udp_socket.recvfrom(1024) # server response
    print("Server: " + response.decode())
    return response, server_address

def tcpsend(tcp_socket, message):
    tcp_socket.send(message.encode())

def tcpreceive(tcp_socket):
    message, server_address = tcp_socket.recvfrom(1024)
    print("Server: ", message.decode())
    return message, server_address

#####################################################

# predefine values
client_id = 'clientB'  # hardcoded client ID: has to be in subscribed users list
secret_key = 200

IP = "127.0.0.1"
UDP_PORT = 1234

# UDP socket creation
server_address = (IP, UDP_PORT)
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # AF_INET = internet, SOCK_DGRAM = UDP
print("\n* UDP socket created\n")

# HELLO
udpsend(udp_socket, server_address, f'HELLO({client_id})')
response, server_address = udpreceive(udp_socket)

# TODO: authentication
#   - receive CHALLENGE, respond with RESPONSE
#   - Generate CK-A key, receive and decrypt the AUTH-SUCCESS message

# TCP Socket
TCP_PORT = 5678
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET: internet, SOCK_STREAM: TCP
tcp_socket.connect((IP, TCP_PORT))
print("\n* TCP socket created\n")  # debug

# CONNECT
rand_cookie = 0
tcpsend(tcp_socket, f'CONNECT({rand_cookie})')
tcpreceive(tcp_socket)

while True:
    msg = input("You: ")
    tcpsend(tcp_socket, msg)
    if msg.strip().lower() == "log off":
        break

tcp_socket.close()
print("* TCP connection closed.")
udp_socket.close()
print("* UDP connection closed.")