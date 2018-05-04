import socket
import sys
import time


class ClientSideRobotArm:
    def __init__(self):
        self.HOST, self.PORT  = "169.254.237.72", 9999
        self.receivedData = ""

        # Established the sokcet object
        self.sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect the socket object to the host and ready to send data
        self.sockt.connect((self.HOST, self.PORT))

    def sendData(self, data):
        # Send input data to host
        self.sockt.sendall(bytes(data, "utf-8"))
        # Recieve the host data
        self.receivedData = str(self.sockt.recv(4096), "utf-8")

if __name__ == '__main__':
    client = ClientSideRobotArm()
    client.sendData("E6-A5")
    print(client.receivedData)
