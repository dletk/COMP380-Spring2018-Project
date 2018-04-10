import socketserver as socketserver
import socket
import time

class RobotArmHandler(socketserver.BaseRequestHandler):
    """
    Request handler for the server of the robot arm

    Override the method handle() to implement communication to the client (robot)
    """
    def handle(self):
        data = self.request.recv(4096)
        string_data = data.decode().strip()
        print(string_data)
        self.request.sendall(bytes("We got your data", "utf-8"))

if __name__ == '__main__':

    HOST, PORT = "192.168.2.2", 9999

    server  = socketserver.TCPServer((socket.gethostname(), PORT), RobotArmHandler)
    print(server.server_address)
    server.serve_forever()
    print("=====> THIS LINE IS AFTER THE SERVER")
