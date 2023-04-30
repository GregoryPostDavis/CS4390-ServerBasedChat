from _thread import *
import socket
import authentication
import encryption
from datetime import datetime

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

def chat(client_id, target_id, session_id):
    while True: # chat starts
        msg = tcpreceive(connection_search[client_id], client_id, cka_search[client_id])
        if "END_REQUEST" in msg: # protocol: receive END_REQUEST(session-id)
            tcpsend(connection_search[target_id], f"END_NOTIF({session_id})", cka_search[target_id], True) # protocol: send END_NOTIF(session-id)
            return
        elif "END_CHECK" in msg:
            return
        tcpsend(connection_search[target_id], f"{client_id}: {msg}", cka_search[target_id], False) # echo the message to the target

def createClientConnection(client_id):
    global connection_search

    print(f"* Accepting {client_id}'s messages...\n")

    while True:
        try:
            msg = tcpreceive(connection_search[client_id], client_id, cka_search[client_id])
            if "CHAT_REQUEST" in msg: # Protocol: CHAT_REQUEST(client-id)
                target_id = msg[13:-1]
                find = [item for item in session_list if target_id in item]
                if target_id in connection_search and len(find) == 0:
                    time = datetime.now()
                    session_id = time.strftime("%Y%m%d%H%M%S") # implementing session id

                    tcpsend(connection_search[client_id], f"CHAT_STARTED({session_id}, {target_id})", cka_search[client_id], True) # Protocol: send CHAT_STARTED(session_id, client_id)
                    tcpsend(connection_search[target_id], f"CHAT_STARTED({session_id}, {client_id})", cka_search[target_id], True)
                    session_list.append((session_id, client_id, target_id))

                    chat(client_id, target_id, session_id)
                    session_list.remove((session_id, client_id, target_id))
                else:
                    tcpsend(connection_search[client_id], f"UNREACHABLE({target_id})", cka_search[client_id], True) # Protocol: send UNREACHABLE(client_id)
            elif "CHAT_CHECK" in msg:
                session_id = msg[11:-1].split(",")[0]
                target_id = msg[11:-1].split(",")[1].strip()
                chat(client_id, target_id, session_id)

            if msg.strip().lower() == "log off":
                print("logging off...\n")
                break
        except OSError:
            continue

    client_socket.close()
    tcp_socket.close()
    print("* TCP connection closed.\n")

#####################################################

# predefined variables
subscriber_list = [('clientA', [100, 5678]),('clientB', [200, 4567]),('clientC', [300, 3456])]
subscriber_search = dict(subscriber_list)
connection_list = [] # (client_id, client_socket)
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
            connection_list.append((client_id, client_socket))
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