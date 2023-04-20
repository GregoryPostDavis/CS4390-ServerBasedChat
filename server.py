import socket
from datetime import datetime
from _thread import *
import queue


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
    now = datetime.now()
    fName = now.strftime("%H.%M.%S.txt")
    f = open(fName, 'a')  # Opens and appends text to file if one does not exist - will be useful when not using Times as names

    connectedTo = " "
    desiredConnection = " "

    # Message Handling from Client
    while True:
        if connectedTo == " ":
            for items in connectionRequests:
                if items == (c_id, desiredConnection):
                    connectedTo = desiredConnection
                    desiredConnection = " "
                    availableClients.remove(c_id)

        while messageQueue.empty():
            msg = tcpreceive(client_socket, c_id)
            if msg.strip().lower() == "log off":
                print("Logging Off...")
                break

            elif msg.strip().lower().startswith("connect"):
                connectTo = msg[7:].strip()
                print("Attempting to connect to ", connectTo)
                if connectTo in subscriber_search and connectTo in availableClients:
                    print("Connecting you to ", connectTo)
                    desiredConnection = connectTo
                    #  availableClients.remove(c_id)
                else:
                    print("Cannot connect you to ", connectTo)

            else:
                # If not a 'log off' message, write to log file
                strToWrite = client_id + ": " + msg
                f.write(strToWrite)
                f.write("\n")
                 #  Add message to message queue
                messageQueue.put((connectedTo, c_id, msg))



        # Message Queue is not empty anymore

        tempQueue = queue.Queue
        for item in list(messageQueue):
            tempQueue.put(item)
        if tempQueue.get[0] == c_id:  # MessageQueue[] contains tuples (To, From, Message)
            tcpsend(client_socket, messageQueue.get()[3])

    client_socket.close()
    tcp_socket.close()
    if c_id in availableClients:
        availableClients.remove(c_id)
    print("* TCP connection closed.")
    return  # Closes Thread


#####################################################

# predefined values
subscriber_list = [('clientA', 100), ('clientB', 200,), ('clientC', 300)]  # predefined subscriber list
subscriber_search = dict(subscriber_list)
subscriber_ports = [('clientA', 1111), ('clientB', 2222), ('clientC', 3333)]  # predefined subscriber ports
port_search = dict(subscriber_ports)

IP = '127.0.0.1'
UDP_PORT = 1234

# Client to Client Connection Values
availableClients = []
messageQueue = queue.Queue() # Format (To, From, Message)
connectionRequests = [] # (connectionA,connectionB)

# UDP socket creation
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # AF_INET: internet, SOCK_DGRAM: UDP
udp_socket.bind((IP, UDP_PORT))
print("\n* UDP socket bound to %s" % (UDP_PORT))  # debug
print("* Waiting for client response...\n")  # debug

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
