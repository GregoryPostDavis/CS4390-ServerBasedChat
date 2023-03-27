import socket
import select # allows utilization of os capabilities

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF = Adress family / INET = internet
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # reconnection if address is already in use

# bind and listen
server_socket.bind((IP, PORT))
server_socket.listen()

# manage list of clients
sockets_list = [server_socket] # clients will be added to this list
clients = {}

# receive messages
print(f'Listening for connections on {IP}:{PORT}...')
def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH) # receive message header
        if not len(message_header):
            return False # if we didn't receive any data (client closed connection)
        message_length = int(message_header.decode("utf-8").strip())
        return {'header': message_header, 'data': client_socket.recv(message_length)}
        
    except:
        # Something went wrong like empty message or client exited abruptly.
        return False
    
# loop
while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list) # read list, write list, error list

    for notified_socket in read_sockets:
        if notified_socket == server_socket: # someone just connected, we need to accept
            client_socket, client_address = server_socket.accept() # get client socket and their address

            user = receive_message(client_socket)
            if user is False: # disconnected
                continue
            
            sockets_list.append(client_socket)
            
            clients[client_socket] = user
            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

        else: # if that wasn't an initial connection, read message.
            message = receive_message(notified_socket)

            if message is False: # empty message because client disconnected
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]
            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            # share message with everybody
            for client_socket in clients:
                if client_socket != notified_socket: # don't send back to the sender
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data']) # send user and message (+ headers)

    # manage socket exceptions
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket) # Remove from list for socket.socket()
        del clients[notified_socket] # Remove from our list of users
