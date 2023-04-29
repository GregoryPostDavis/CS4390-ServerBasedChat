from _thread import *
import socket
import authentication
import encryption
import curses

def udpsend(udp_socket, server_address, message):
    udp_socket.sendto(message.encode(), server_address)
    print("You: " + message)

def udpreceive(udp_socket):
    response, server_address = udp_socket.recvfrom(1024) # server response
    print("Server: " + response.decode())
    return response, server_address

def tcpsend(tcp_socket, message, ck_a):
    tcp_socket.send(encryption.encrypt_msg(ck_a, message).encode())

def tcpreceive(tcp_socket, ck_a, bool):
    message, server_address = tcp_socket.recvfrom(1024)
    message = encryption.decrypt_msg(message.decode(), ck_a)
    if bool:
        print("Server: ", message) # receiving messages from the server
    else:
        print(message) # receiving messages from another user
    return message, server_address

def receive(tcp_socket, ck_a):
    global session_id
    
    while True:
        msg, server_address = tcpreceive(tcp_socket, ck_a, False)
        if "CHAT_STARTED" in msg: # Protocol: receive CHAT_STARTED(session_id, client_id)
           session_id = msg[13:-1].split(",")[0]
        if "END_NOTIF" in msg:
            print("\n* Chat ended\n")
            return

#####################################################

# predefined variables
session_id = None

# UDP socket creation
IP = '127.0.0.1'
UDP_PORT = 1234

server_address = (IP, UDP_PORT)
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("\n* UDP socket created\n")

while True:
    val = input("Type 'log on' or 'log off': ")
    if(val.strip().lower() == "log off"):
        udp_socket.close()
        print("* UDP connection closed.")
        exit()
    elif(val.strip().lower() == "log on"):

        client_id = input("Enter username: ") #Has to be in subscribed users list
        secret_key = input("Enter secret key: ")                  # LOG ON
        print()

        # Logged on
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
        
        # TCP Socket establishment
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect((IP, TCP_PORT))
        print("\n* TCP socket created\n")                               # - DEBUG

        tcpsend(tcp_socket, f"CONNECT({RAND_COOKIE})", ck_a) # Protocol: send CONNECT(rand_cookie)
        tcpreceive(tcp_socket, ck_a, True) # Protocol: receive CONNECTED
        print("Commands:\n1. Log off: to log off and end connection with the server\n2. Chat (client-ID): to start a chat with another user\n3. End Chat: to end a current chat\n4. History (client-ID): check your past chat messaged exchanged with another user\n")

        while True:
            start_new_thread(receive, (tcp_socket, ck_a)) # receive messages

            msg = input("") # Send messages

            # message check
            if msg.strip().lower().startswith('chat'):
                target = msg.split(" ")[1]
                tcpsend(tcp_socket, f"CHAT_REQUEST({target})", ck_a) # Protocol: send CHAT_REQUEST(client_id)
                print(f"You: CHAT_REQUEST({target})") 
            elif msg.strip().lower().startswith('end chat'):
                tcpsend(tcp_socket, f"END_REQUEST({session_id})", ck_a) # Protocol: send END_REQUEST(session_ID)
                print("\n* Chat ended\n")
            else:
                tcpsend(tcp_socket, msg, ck_a)
            if msg.strip().lower() == "log off":
                print("Logging off...\n")
                break
        break

tcp_socket.close()
print("* TCP connection closed.")

udp_socket.close()
print("* UDP connection closed.")