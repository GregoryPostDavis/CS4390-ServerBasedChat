import socket

PORT = 1234

server_socket = socket.socket()
print ("Socket successfully created")

server_socket.bind(('', PORT)) # empty IP so the server listens to requests
print ("socket binded to %s" %(PORT))
server_socket.listen(5) # listen to new connections
print ("socket is listening")

# loop
while True:
    client, addr = server_socket.accept()
    print ('Got connection from', addr )
    client.send('Thank you for connecting'.encode())
    client.close()

    break # connection closed