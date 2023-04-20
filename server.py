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
    f = open(fName,
             'a')  # Opens and appends text to file if one does not exist - will be useful when not using Times as names

    # Connection
    connectedTo = "unreachableValue"
    desiredConnection = " "

    # Message Handling from Client
    while True:
        if connectedTo == "unreachableValue":
            for items in connectionRequests:
                if items[0] == c_id and items[1] == desiredConnection:
                    connectedTo = items[1]
                    desiredConnection = " "
                    print("You have been connected to ", items[1])
                    availableClients.remove(c_id)
                    connectionRequests.remove(items)
                    connection_list.append((c_id, client_socket))

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
                connection_list.remove((c_id, client_socket))
                client_socket.close()
                tcp_socket.close()
                print("* TCP connection closed.")
                return  # Closes Thread

            elif msg.strip().lower().startswith("connect"):
                connectTo = msg[7:].strip()
                # print("Sending a Connection Request ", connectTo)
                if connectTo in subscriber_search and connectTo in availableClients:
                    print("Sending a connection request to connect with ", connectTo)
                    desiredConnection = connectTo
                    connectionRequests.append((connectTo, c_id, client_socket))
                else:
                    print("Cannot connect you to ", connectTo)

            elif msg:
                # If not a 'log off' message, write to log file
                strToWrite = client_id + ": " + msg
                f.write(strToWrite)
                f.write("\n")
                #  Add message to message queue
            messageQueue.put((connectedTo, c_id, msg))  #  Destination, Source, Message

        # Message Queue is not empty anymore

        # tempQueue = queue.Queue
        # for item in list(messageQueue):
        # tempQueue.put(item)
        # if tempQueue.get[0] == c_id:  # MessageQueue[] contains tuples (To, From, Message)
        # tcpsend(client_socket, messageQueue.get()[3])

        #  Try passing the socket into the message queue and having a thread iterate through messageQueue


def messageHandler():
    print("Message Handler Started")
    while True:
        if not messageQueue.empty():
            #print("Message in Queue")
            currentMessage = messageQueue.get()
            print(currentMessage[2])
            if currentMessage[0] in connection_search:

                tcpsend(connection_search.get(currentMessage[0]), currentMessage[2])


#####################################################

# predefined values
subscriber_list = [('clientA', 100), ('clientB', 200,), ('clientC', 300)]  # predefined subscriber list
subscriber_search = dict(subscriber_list)
subscriber_ports = [('clientA', 1111), ('clientB', 2222), ('clientC', 3333)]  # predefined subscriber ports
port_search = dict(subscriber_ports)
connection_list = []
connection_search = dict(connection_list)

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

# Create TCP Sockets and Threads
while True:
    # HELLO
    message, client_address = udpreceive(udp_socket)
    client_id = message[6:-1]  # extract the client ID

    start_new_thread((messageHandler), ())

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
