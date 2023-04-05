import socket

def udpsend(udp_socket, server_address, message):
    udp_socket.sendto(message.encode(), server_address)
    print("You: " + message)

def udpreceive(udp_socket):
    response, server_address = udp_socket.recvfrom(1024) # server response
    print("Server: " + response.decode())
    return response, server_address

def tcpsend(tcp_socket, message):
    tcp_socket.send(message.encode('utf-8'))
    print("You: " + message)

def tcpreceive(tcp_socket):
    message, server_address = tcp_socket.recvfrom(1024)
    print('Server: ', message.decode('utf-8'))
    return message, server_address

#####################################################

# predefine values
client_id = 'clientA'  # hardcoded client ID: has to be in subscribed users list
secret_key = 100

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

tcpsend(tcp_socket, "Hello Server!")
tcpreceive(tcp_socket)

# TODO: connection
    #   - send CONNECT, receive CONNECTED

udp_socket.close()