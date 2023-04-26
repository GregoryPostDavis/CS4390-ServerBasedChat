import socket
from datetime import datetime   # FOR SESSION-ID
from _thread import *
import queue
import threading            # FOR CHAT HISTORY BOOLEAN VARIABLE
import chatHistory
import authentication
import encryption
import os.path              # FOR CHECKING IF CHAT HISTORY FILE EXISTS

def udpsend(udp_socket, client_address, message):
    udp_socket.sendto(message.encode(), client_address)
    print("You: " + message)  # debug


def udpreceive(udp_socket):
    message, client_address = udp_socket.recvfrom(1024)  # receive HELLO message
    message = message.decode()
    print("Client: " + message)
    return message, client_address


def tcpsend(client_socket, message):
    print("You: " + message)
    client_socket.send(message.encode())  # TODO: the encoding will be replaced with CK-A


def tcpreceive(client_socket, client_id):
    message = client_socket.recv(1024).decode()
    print(f"{client_id}: " + message)  # buffer size not that important, if it goes over it will be saved
    return message


def createClientConnection(c_id, c_addr):
    # TCP Socket
    TCP_PORT = port_search.get(c_id, None)  # get the port from the dedicated port list
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # #AF_INET: internet, SOCK_STREAM: TCP
    tcp_socket.bind((IP, TCP_PORT))
    tcp_socket.listen()

    client_socket, address = tcp_socket.accept()  # Returns client socket and address
    print("\n* TCP socket bound to %s\n" % (TCP_PORT))

    # CONNECT
    rand_cookie = 0
    msgs = tcpreceive(client_socket, c_id)
    if str(rand_cookie) == msgs[8:-1]:
        tcpsend(client_socket, "CONNECTED\n")
        availableClients.append(c_id)

    # Message Logging (To Text File)
    # now = datetime.now()
    # fName = now.strftime("%H.%M.%S.txt")
    # f = open(fName, 'a')  # Opens and appends text to file if one does not exist

    # Connection
    connectedTo = "unreachableValue"
    desiredConnection = " "

    # Message Handling from Client
    while True:
        if connectedTo == "unreachableValue":  # Default Value - Only used if no connection has been made
            for items in connectionRequests:
                if items[0] == c_id and items[1] == desiredConnection:
                    connectedTo = items[1]
                    desiredConnection = " "  # Resets this value just to be safe
                    # print("You have been connected to ", items[1])
                    #tcpsend(tcp_socket, "CHAT_STARTED\n")
                    connection_list.append(c_id)
                    availableClients.remove(c_id)
                    connectionRequests.remove(items)
        else:
            if desiredConnection in availableClients:
                connection_list.remove(c_id)
                connection_list.remove(connectedTo)
                desiredConnection = " "
                connectedTo = "unreachableValue"
                availableClients.append(c_id)

        client_socket.settimeout(.5)
        # msg = tcpreceive(client_socket, c_id)  # Not using this because we need it to timeout
        try:
            msg = client_socket.recv(1024).decode()
        except socket.timeout:
            # no message received
            pass
        else:
            if msg.strip().lower() == "log off":
                # Close Everything Important and remove visibility for other clients
                print("Logging Off...")
                if c_id in availableClients:
                    availableClients.remove(c_id)
                client_socket.close()
                tcp_socket.close()
                print("* TCP connection closed.")
                connected.clear()                       # SET TO FALSE & USED FOR CHAT HISTORY FEATURE
                return  # Closes Thread

            elif msg.strip().lower().startswith("connect"):
                connectTo = msg[7:].strip()
                # print("Sending a Connection Request ", connectTo)
                if connectTo in subscriber_search and connectTo in availableClients:
                    print("Sending a connection request to connect with ", connectTo)
                    desiredConnection = connectTo
                    connectionRequests.append((connectTo, c_id.strip(), client_socket))
                    connected.set()                    # SET TO TRUE & USED FOR CHAT HISTORY FEATURE
                    filename = authentication.simple_hash(encryption.encrypt_msg(c_id, connectTo))    # GENERATES CHAT HISTORY FILE NAME
                else:
                    print("Cannot connect you to ", connectTo)
                    messageQueue.put(c_id, c_id, "UNREACHABLE")

            elif msg.strip() == "END_REQUEST":
                connection_list.remove(c_id)
                connection_list.remove(connectedTo)
                desiredConnection = " "
                connectedTo = "unreachableValue"
                availableClients.append(c_id)
                connected.clear()                    # SET TO FALSE & USED FOR CHAT HISTORY FEATURE

            elif msg.lower().startswith("history"):                       # CHAT HISTROY FEATURE
                    if msg[7:].strip().lower() == c_id.strip().lower():
                        messageQueue.put((c_id, c_id, "CANNOT SEND CHAT HISTORY TO YOURSELF!"))
                        pass
                    elif msg[7:].strip().lower() != connectedTo.strip().lower():
                            messageQueue.put((c_id, c_id, "YOU ARE NOT IN SEESION WITH <" + msg[7:] + ">"))
                            pass
                    else:
                        if os.path.isfile(filename):                      # CHECKS IF CHAT HISTORY FILE EXISTS
                            print("File exists")
                            lines = chatHistory.readhistory(filename)
                            for line in lines:
                                messageQueue.put((c_id,c_id,line))
                                pass
                            pass
                        else:
                            print("File does not exist")
                            messageQueue.put((c_id,c_id,"CHAT HISTORY DOES NOT EXIST YET!"))
                        

            elif msg:
                #pass
                # If not a 'log off' message, write to log file
                # strToWrite = client_id + ": " + msg
                # f.write(strToWrite)
                # f.write("\n")
                #  Add message to message queue
                #print("connectedTo: " + connectedTo)
                messageQueue.put((connectedTo, c_id, msg))  # Destination, Source, Message

                if connected.is_set():                                  # IF TWO CLIENTS ARE CONNECTED (CONNECTED IS TRUE)
                    #print("connectedTo: " + connectedTo)
                    #if connectedTo == "unreachableValue":              # WIP
                    chatHistory.write(filename, c_id, msg)              # ADDS CHAT TO HISTORY          # NEEDS TO IMPLEMENT SESSION-ID
            


def messageHandler():
    # print("Message Handler Started")
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        if not messageQueue.empty():
            # print("Message in Queue")
            currentMessage = messageQueue.get()
            if currentMessage[2].lower().startswith("connect"):
                if currentMessage[0].strip().lower() == currentMessage[1].strip().lower():
                    pass
                elif currentMessage[2][7:].strip().lower() in recv_search:
                    RECV_PORT = recv_search.get(currentMessage[2][7:])
                    tcp_sock.connect((IP, RECV_PORT))
                    tcpsend(tcp_sock, ("CHAT_REQUEST", currentMessage[1]))
                    tcp_sock.close()
                    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            elif currentMessage[0] == "unreachableValue":
                pass  # ignores messages that are sent to "nobody"
            elif currentMessage[2] == "END_REQUEST":
                RECV_PORT = recv_search.get(currentMessage[0])
                tcp_sock.connect((IP, RECV_PORT))
                tcpsend(tcp_sock, "END_NOTIF")
                tcp_sock.close()
                tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
           
            else:
                RECV_PORT = recv_search.get(currentMessage[0])
                # print(currentMessage[0]) debug
                # print(RECV_PORT) debug
                tcp_sock.connect((IP, RECV_PORT))
                tcpsend(tcp_sock, currentMessage[2])        
                tcp_sock.close()
                tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # print(currentMessage[2])


#####################################################

# predefined values
subscriber_list = [('clientA', 100), ('clientB', 200,), ('clientC', 300), ('clientD', 400)]  # predefined subscriber list
subscriber_search = dict(subscriber_list)
subscriber_ports = [('clientA', 4000), ('clientB', 4010), ('clientC', 4020), ('clientD', 4030)]  # predefined subscriber ports
port_search = dict(subscriber_ports)
recv_ports = [("clientA", 4100), ("clientB", 4200), ("clientC", 4300), ('clientD', 4400)]  # predefined subscriber ports
recv_search = dict(recv_ports)
connection_list = []
connection_search = dict(connection_list)
connected = threading.Event()        # BOOLEAN VARIABLE SET FALSE BY DEFAULT FOR CHAT HISTORY FEATURE

IP = '127.0.0.1'
UDP_PORT = 1234

# Client to Client Connection Values
availableClients = []
messageQueue = queue.Queue()  # Format (To, From, Message)
connectionRequests = []  # (connectionA,connectionB, socketA)

# UDP socket creation
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # AF_INET: internet, SOCK_DGRAM: UDP
udp_socket.bind((IP, UDP_PORT))
print("\n* UDP socket bound to %s" % (UDP_PORT))  # debug
print("* Waiting for client response...\n")  # debug

start_new_thread(messageHandler, ())  # Message Handling is done in its own thread

# Create TCP Sockets and Threads
while True:
    # HELLO
    message, client_address = udpreceive(udp_socket)
    client_id = message[6:-1]  # extract the client ID

    # Verification
    if client_id in subscriber_search:
        udpsend(udp_socket, client_address, f"Hello, {client_id}! Welcome to the server!")
        start_new_thread(createClientConnection, (client_id, client_address))

        # TODO: authentication
        #   - retrieve the client's secret key
        #   - send CHALLENGE message
        #   - receive RESPONSE
        #   - if failure: send AUTH-FAIL message
        #   - if success: generate encryption key CK-A and send AUTH-SUCCESS encrypted in that key

    else:
        print("* Client is not in the subscriber list.")

udp_socket.close()
print("* UDP connection closed.")
