from _thread import *
import socket
import authentication
import encryption
import chatHistory
import os.path
from datetime import datetime
import time

def udpsend(udp_socket, client_address, message):
    udp_socket.sendto(message.encode(), client_address)
    print("You: " + message)

def udpreceive(udp_socket):
    message, client_address = udp_socket.recvfrom(1024)
    message = message.decode()
    print("Client: " + message)
    return message, client_address

def tcpsend(tcp_socket, message, ck_a, bool):
    if bool == True:
        print("You: " + message)
    tcp_socket.send(encryption.encrypt_msg(ck_a, message).encode())

def tcpreceive(client_socket, client_id, ck_a):
    message = encryption.decrypt_msg(client_socket.recv(1024).decode(), ck_a)
    print(f"{client_id}: " + message)
    return message

def printHistory(client_id, message):
    target_hist = message[12:-1]
    print("History target: ", target_hist)
    filename1 = client_id + target_hist
    filename2 = target_hist + client_id
    print("Filenames: ", filename1, ", ", filename2)

    if target_hist == client_id:
        tcpsend(connection_search[client_id][0], "SERVER: Cannot send chat history to yourself!" , cka_search[client_id], False)
        return
    if os.path.isfile(filename1):
        print("CHAT LOG EXISTS")
        lines = chatHistory.readhistory(filename1)
        for line in lines:
            tcpsend(connection_search[client_id][0], line , cka_search[client_id], False)
            time.sleep(0.01)
    elif os.path.isfile(filename2):
        print("CHAT LOG EXISTS")
        lines = chatHistory.readhistory(filename2)
        for line in lines:
            tcpsend(connection_search[client_id][0], line , cka_search[client_id], False)
            time.sleep(0.01)
    else:
        print("CHAT LOG DOES NOT EXIST")
        tcpsend(connection_search[client_id][0], "SERVER: chat history does not exist yet!" , cka_search[client_id], False)

def chat(client_id, target_id, session_id):
    while True: # chat starts
        msg = tcpreceive(connection_search[client_id][0], client_id, cka_search[client_id])

        if "HISTORY_REQ" in msg: # Protocol: receive HISTORY_REQ(client-ID)
            printHistory(client_id, msg)
        elif "END_REQUEST" in msg: # protocol: receive END_REQUEST(session-id)
            tcpsend(connection_search[target_id][0], f"END_NOTIF({session_id})", cka_search[target_id], True) # protocol: send END_NOTIF(session-id)
            return
        elif "END_CHECK" in msg:
            return
        elif msg:
            filename1 = client_id + target_id
            filename2 = target_id + client_id
            if os.path.isfile(filename1):
                chatHistory.write(session_id, filename1, client_id, msg) # adds chat to history
            elif os.path.isfile(filename2):
                chatHistory.write(session_id, filename2, client_id, msg) # adds chat to history
            else: # if there is no file
                print("Creating new history file.")
                chatHistory.write(session_id, filename1, client_id, msg) # adds chat to history
            tcpsend(connection_search[target_id][0], f"{client_id}: {msg}", cka_search[target_id], False) # echo the message to the target

def createClientConnection(client_id):
    global connection_search, session_list

    print(f"* Accepting {client_id}'s messages...\n")

    while True:
        msg = tcpreceive(connection_search[client_id][0], client_id, cka_search[client_id])
        if "CHAT_REQUEST" in msg: # Protocol: CHAT_REQUEST(client-id)
            target_id = msg[13:-1]
            find = [item for item in session_list if target_id in item]
            if target_id in connection_search and len(find) == 0:
                time = datetime.now()
                session_id = time.strftime("%Y%m%d%H%M%S") # implementing session id

                tcpsend(connection_search[client_id][0], f"CHAT_STARTED({session_id}, {target_id})", cka_search[client_id], True) # Protocol: send CHAT_STARTED(session_id, client_id)
                tcpsend(connection_search[target_id][0], f"CHAT_STARTED({session_id}, {client_id})", cka_search[target_id], True)
                session_list.append((session_id, client_id, target_id))

                chat(client_id, target_id, session_id) # chatting...
                session_list.remove((session_id, client_id, target_id))
            else:
                tcpsend(connection_search[client_id][0], f"UNREACHABLE({target_id})", cka_search[client_id], True) # Protocol: send UNREACHABLE(client_id)
        elif "CHAT_CHECK" in msg:
            session_id = msg[11:-1].split(",")[0]
            target_id = msg[11:-1].split(",")[1].strip()
            chat(client_id, target_id, session_id)
        if "HISTORY_REQ" in msg: # Protocol: receive HISTORY_REQ(client-ID)
            printHistory(client_id, msg)
        if msg.strip().lower() == "log off":
            print(f"logging off {client_id}...\n")
            break

    connection_search[client_id][0].close() # client_socket close
    connection_search[client_id][1].close() # tcp_socket close
    print(f"* TCP connection for {client_id} closed.\n")

    for clients in connection_list:
        if clients[0] == client_id:
            connection_list.remove(clients)
    connection_search = dict(connection_list)

    return

#####################################################

# predefined variables
subscriber_list = []
numA = 100
numB = 2000
for i in range(10): # for 10 default clients
    client_name = f'client{chr(ord("A")+i)}'
    subscriber_list.append((client_name, [numA, numB]))
    numA += 100
    numB += 10
subscriber_search = dict(subscriber_list)
connection_list = [] # (client_id, [client_socket, tcp_socket])
connection_search = dict(connection_list)
cka_list = [] # (client_id, ck_a)
cka_search = dict(cka_list)
session_list = [] # (session_id, clientA, clientB)

# UDP socket creation
IP = '127.0.0.1'
UDP_PORT = 1234

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((IP, UDP_PORT))
print("\n* UDP socket bound to %s" %(UDP_PORT))
print("* Waiting for client connection...\n")

while True:

    # Client log on
    message, client_address = udpreceive(udp_socket) # Protocol: receive HELLO(client_ID)
    client_id = message[6:-1]  # extract the client ID

    # Verification
    if client_id in subscriber_search:
        # Authentication
        RAND_COOKIE, xres = authentication.server_hash(subscriber_search[client_id][0])
        udpsend(udp_socket, client_address, f"CHALLENGE({RAND_COOKIE})") # Protocol: send CHALLENGE(rand)

        message, client_address = udpreceive(udp_socket) # Protocol: receives RESPONSE(client_ID, res)
        res = message[18:-1]
        
        # Checking xres and res
        if authentication.check_hash(xres, res):
            TCP_PORT = subscriber_search[client_id][1] # temporary port allocation
            # Encryption
            ck_a = encryption.cipher_key(RAND_COOKIE, subscriber_search[client_id][0])
            cka_list.append((client_id, ck_a))
            cka_search = dict(cka_list)
            message = f"AUTH_SUCCESS({RAND_COOKIE}, {TCP_PORT})"
            print("You: " + message)
            udp_socket.sendto(encryption.encrypt_msg(ck_a, message).encode(), client_address) # Protocol: send AUTH_SUCCESS(rand_cookie, port_number)
        
            # TCP connection
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tcp_socket.bind((IP, TCP_PORT))
            tcp_socket.listen()
            client_socket, address = tcp_socket.accept() # Returns client socket and address
            print(f"\n* TCP socket bound to {TCP_PORT}\n")
            connection_list.append((client_id, [client_socket, tcp_socket]))
            connection_search = dict(connection_list)

            # TCP Socket
            message = tcpreceive(client_socket, client_id, ck_a) # Protocol: receive CONNECT(rand_cookie)
            if str(RAND_COOKIE) == message[8:-1]: # Protocol: send CONNECTED
                tcpsend(client_socket, "CONNECTED\n", ck_a, True)

            start_new_thread(createClientConnection, (client_id, ))
        else:
            udpsend(udp_socket, client_address, "AUTH_FAIL")
            print()

    else:
        udpsend(udp_socket, client_address, f"Not on subscriber list.\n")

udp_socket.close()
print("* UDP connection closed.")