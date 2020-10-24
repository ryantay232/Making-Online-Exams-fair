import socket

# Client script for testing
s = socket.socket()
host = 'change to your IP address'
port = 5050

s.connect((host, port))

while True:
    read = input()
    s.send(str.encode(read))
