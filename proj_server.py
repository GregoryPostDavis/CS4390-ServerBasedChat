import socket

IP = "127.0.0.1"
PORT = 1234

# Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # AF_INET: internet, SOCK_DGRAM: UDP
print("Socket successfully created")  # debug

server_socket.bind((IP, PORT))
print("Socket bound to %s" %(PORT))  # debug
print("Waiting for client response...")  # debug

# receiving data from client
while True:
    message, client_address = server_socket.recvfrom(1024) # receive HELLO message
    message = message.decode()
    client_id = message[6:-1]  # extract the client ID

    response_message = f'Hello, {client_id}! Welcome to the server!'
    server_socket.sendto(response_message.encode(), client_address)  # Response message
    print("Connection established with client")  # debug

    break  # connection closed

# TCP Socket
TCP_IP = "127.0.0.1"
TCP_PORT = 5678

tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # #AF_INET: internet, SOCK_STREAM: TCP
tcp_server.bind((TCP_IP, TCP_PORT))
tcp_server.listen()


while True:
    client, address = tcp_server.accept()  # Returns client socket and address
    print(f"Connected to {address}")
    print(client.recv(1024).decode('utf-8'))  # buffer size not that important, if it goes over it will be saved
                                              # make sure to encode with utf -8 as well
    client.send("Hello Client!".encode('utf-8'))
    print(client.recv(1024).decode('utf-8'))
    client.send("Bye!".encode('utf-8'))
    client.close()
    break  # connection closed
