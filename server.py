import socket
import authentication
import encryption
from _thread import *
import queue
import time


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

def testSend(tcp_socket, message):
    tcp_socket.send(message)

def tcpreceive(client_socket, client_id, ck_a):
    message = encryption.decrypt_msg(client_socket.recv(1024).decode(), ck_a)
    print(f"{client_id}: " + message)
    return message


def createClientConnection(c_id, c_addr):
    # TCP Socket
    TCP_PORT = subscriber_search.get(c_id, None)[1]
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((IP, TCP_PORT))
    tcp_socket.listen()

    cka = cka_search.get(c_id)

    client_socket, address = tcp_socket.accept()  # Returns client socket and address
    print("\n* TCP socket bound to %s\n" % (TCP_PORT))


    msgs = tcpreceive(client_socket, c_id, cka_search.get(c_id))
    if str(RAND_COOKIE) == msgs[8:-1]: # Protocol: send CONNECTED
        try:
            tcpsend(client_socket, "CONNECTED\n", ck_a)
            availableClients.append(c_id)
        except:
            tcp_socket.close()
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.bind((IP, TCP_PORT))
            time.sleep(.1)
            tcpsend(tcp_socket, "CONNECTED\n", ck_a)

    #Connection
    connectedTo = "unreachableValue"
    desiredConnection = " "

    print("I make it here")

    # Message handling from Client
    while True:
        if connectedTo == "unreachableValue":  # Default value - only used if no connection has been made
            for requests in connectionRequests:
                if requests[0] == c_id and requests[1] == desiredConnection:
                    connectedTo = requests[1]
                    # desiredConnection = " "  # Resets this just to be safe
                    connection_list.append(c_id)
                    availableClients.remove(c_id)
                    connectionRequests.remove(requests)
                    messageQueue.put((c_id, c_id, (encryption.encrypt_msg(ck_a, ("CHAT STARTED(" + connectedTo + ")"))).encode()))
                else:
                    if c_id not in connection_list:
                        print(c_id, requests[0], desiredConnection, requests[1])
                        time.sleep(2)
                        # Reset Default Values
                        desiredConnection = " "
                        connectedTo = "unreachableValue"
                        if c_id not in availableClients:
                            availableClients.append(c_id)
            client_socket.settimeout(.5)  # Don't use tcpreceive because we need to timeout
            try:
                msg = client_socket.recv(1024)
                msg = encryption.decrypt_msg(msg.decode(), cka)
                # print(msg)
            except socket.timeout:
                pass  # No messages received in the timeout interval
            else:
                # print("msg rcvd")
                if msg.strip().lower() == "log off":
                    # Close Everything important and remove visibility from other clients
                    if connectedTo != "unreachableValue":
                        messageQueue.put((connectedTo, c_id, (encryption.encrypt_msg(ck_a, "END_NOTIF").encode())))
                        connection_list.remove(c_id)
                        connection_list.remove(connectedTo)
                        pass
                    if c_id in availableClients:
                        availableClients.remove(c_id)
                    if c_id in connection_list:
                        connection_list.remove(c_id)

                    client_socket.close()
                    tcp_socket.close()
                    print("* TCP connection closed.")
                    return

                elif msg.strip().lower().startswith("connect"):
                    connectTo = msg[7:].strip()
                    if connectTo in subscriber_search and connectTo in availableClients:
                        print("Sending a connection request to", connectTo)
                        desiredConnection = connectTo
                        connectionRequests.append((connectTo.strip(), c_id.strip(), client_socket))
                    else:
                        print("Cannot connect you to ", connectTo)
                        messageQueue.put((c_id, c_id, encryption.encrypt_msg(ck_a, ("UNREACHABLE " + connectedTo)).encode()))

                elif msg.strip() == "END_REQUEST":
                    messageQueue.put((connectedTo, c_id, encryption.encrypt_msg(ck_a, ("END_NOTIF")).encode()))
                    connection_list.remove(c_id)
                    connection_list.remove(connectedTo)
                    desiredConnection = " "
                    connectedTo = "unreachableValue"
                    availableClients.append(c_id)
                elif msg:
                    pass

                #Message Handling
                print("Putting message in queue")
                messageQueue.put((connectedTo, c_id, encryption.encrypt_msg(ck_a, msg).encode()))




def messageHandler():
    print("Message Handler Started")
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        if not messageQueue.empty():
            print("Message in Queue")
            encryptedMessage = messageQueue.get()
            currentMessage = encryption.decrypt_msg(encryptedMessage[2].decode(), ck_a)
            if currentMessage[2].lower().startswith("connect "):
                if currentMessage[0].strip().lower() == currentMessage[1].strip.lower():
                    pass  # ignore clients trying to connect to themselves
                elif currentMessage[2][7:].strip().lower() in subscriber_search:
                    RECV_PORT = subscriber_search.get(currentMessage[2][2][7:])
                    tcp_sock.connect((IP, RECV_PORT))
                    tcpsend(tcp_sock, ("CHAT REQUEST", currentMessage[1]), ck_a)
                    tcp_sock.close()
                    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                elif currentMessage[0] == "unreachableValue":
                    print(currentMessage[2])
                    pass  # ignore messages that are sent to nobody
                elif currentMessage[2] == "END_REQUEST":
                    RECV_PORT = subscriber_search.get(currentMessage[0][2])
                    tcp_sock.connect((IP, RECV_PORT))
                    tcpsend(tcp_sock, "END_NOTIF", ck_a)
                    tcp_sock.close()
                    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                else:
                    RECV_PORT = subscriber_search.get(currentMessage[0][2])
                    tcp_sock.connect((IP, RECV_PORT))
                    if currentMessage[0] == currentMessage[1]:
                        tcpsend(tcp_sock, ("Server: " + currentMessage[2]), ck_a)
                    else:
                        tcpsend(tcp_sock, (currentMessage[1] + ": " + currentMessage[2]), ck_a)
                        tcp_sock.close()
                        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#####################################################


# predefined subscribers
subscriber_list = [('clientA', (100,4000,4100)),('clientB', (200,4010,4110)),('clientC', (300,4020,4120))]  # (ID, (Secret Key, Snd Port, Rec Port))
subscriber_search = dict(subscriber_list)
cka_list = []
cka_search = dict(cka_list)

# Client to Server and Client to Client Connection Values
connection_list = []
connection_search = dict(connection_list)
availableClients = []
connectionRequests = []
messageQueue = queue.Queue()  # Format (To, From, Message)


# UDP socket creation
IP = '127.0.0.1'
UDP_PORT = 1234

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((IP, UDP_PORT))
print("\n* UDP socket bound to %s" %(UDP_PORT))
print("* Waiting for client response...\n")

start_new_thread(messageHandler, ())

# Client log on
while True:
    message, client_address = udpreceive(udp_socket) # Protocol: receive HELLO(client_ID)
    client_id = message[6:-1]  # extract the client ID

    print(f"The client id is {client_id}")

    # Verification
    if client_id in subscriber_search:
        # Authentication
        RAND_COOKIE, xres = authentication.server_hash(subscriber_search[client_id][0])
        print(f"The xres is {xres}")
        udpsend(udp_socket, client_address, f"CHALLENGE({RAND_COOKIE})") # Protocol: send CHALLENGE(rand)

        message, client_address = udpreceive(udp_socket) # Protocol: receives RESPONSE(client_ID, res)
        res = message[18:-1]
        print(f"The response is {res}")

        # Checking xres and res
        if authentication.check_hash(xres, res):
            TCP_PORT = subscriber_search.get(client_id)[1]  # temporary port allocation
            REC_PORT = subscriber_search.get(client_id)[2]  # temporary listening port allocation
            # Encryption
            ck_a = encryption.cipher_key(RAND_COOKIE, subscriber_search[client_id][0])
            cka_list.append((client_id, ck_a))
            cka_search = dict(cka_list)

            message = f"AUTH_SUCCESS({RAND_COOKIE}, {TCP_PORT}, {REC_PORT})"
            print("You: " + message)
            udp_socket.sendto(encryption.encrypt_msg(ck_a, message).encode(), client_address) # Protocol: send AUTH_SUCCESS(rand_cookie, port_number)

            start_new_thread(createClientConnection, (client_id, client_address))
        else:
            udpsend(udp_socket, client_address, "AUTH_FAIL")

    else:
        print("* Client is not in the subscriber list.")
        udpsend(udp_socket, client_address, "AUTH_FAIL")

udp_socket.close()
print("* UDP connection closed.")