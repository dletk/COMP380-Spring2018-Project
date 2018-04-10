import socket
import sys
import time

HOST, PORT  = "169.254.32.111", 9999
data = " ".join(sys.argv[1:])

# Create a socket to communicate with the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    sock.sendall(bytes(data + "\n", "utf-8"))
    # Receive data from the server and shut down
    receive = str(sock.recv(1024), "utf-8")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket2:
    socket2.connect((HOST, PORT))
    socket2.sendall(bytes("1", "utf-8"))
    receive = str(socket2.recv(1024), "utf-8")
    receive = "BACK"


print(receive)
