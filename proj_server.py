import socket

IP = "127.0.0.1"
PORT = 1234

# Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # AF_INET: internet, SOCK_DGRAM: UDP
print ("Socket successfully created") # debug

server_socket.bind((IP, PORT))
print ("socket binded to %s" %(PORT)) # debug
print("Waiting for client response...")  # debug

# receiving data from client
while True:
    message, client_address = server_socket.recvfrom(1024) # receive HELLO message
    message = message.decode()
    client_id = message[6:-1]  # extract the client ID

    response_message = f'Hello, {client_id}! Welcome to the server!'
    server_socket.sendto(response_message.encode(), client_address) # Response message

    break # connection closed