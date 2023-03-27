import socket

server_socket = socket.socket()
port = 1234
server_socket.connect(('127.0.0.1', port))
print (s.recv(1024).decode())

server_socket.close()