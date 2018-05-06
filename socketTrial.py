import socketserver as socketserver
import socket
import time
from RobotArm import *


class RobotArmHandler(socketserver.BaseRequestHandler):
    """
    Request handler for the server of the robot arm

    Override the method handle() to implement communication to the client (robot)
    """

    def handle(self):
        # The form of data recieve will be a string "Pos1-Pos2", example: "E9-D7"
        data = self.request.recv(4096)
        # Decode the data to actual string
        string_data = data.decode().strip()
        move = string_data.split("-")

        first_position = move[0]
        second_position = move[1]

        print(first_position)
        print(second_position)

        self.movePiece(first_position, second_position)

        self.request.sendall(bytes("done", "utf-8"))

    def movePiece(self, pos1, pos2):
        """Method to move a piece from pos1 to pos2"""

        initialRow = {"A": (7, 0), "B": (6, 0), "C": (6, 0), "D": (
            6, 0), "E": (6, 0), "F": (6, 2), "G": (7, -1), "H": (8, 0)}
        turningAngle = {"A": -43, "B": -60, "C": -70, "D": -85, "E": -97, "F": -110, "G": -125, "H": -140}

        # Find the column of the positions
        col1 = pos1[0]
        col2 = pos2[0]
        # Find the row of the fist position
        row1 = int(pos1[1])
        row2 = int(pos2[1])

        # Turn to the column of the first position
        robot.turnExact(turningAngle[col1])

        # Take out the initial row after turning to col1 with the uncertainty
        initialRowAndIncorrect1 = initialRow[col1]
        initialRowAndIncorrect2 = initialRow[col2]
        currentRow = initialRowAndIncorrect1[0]

        # Move the arm to row1
        incorrect = initialRowAndIncorrect1[1]
        traveledDistance = 0
        traveledDistance += self.moveArmToRow(currentRow, row1, 0, incorrect)
        # Pick up the object
        self.pickOrDropPiece()

        # Now the object is currently at col1, we need to turn it to col2
        robot.turnExact(turningAngle[col2] - turningAngle[col1])

        # NOTE: Here, because we measture the angles continuously, after the arm moving to the first
        # row, row1 and col1, when it turn back that much degree, it has already gone a distance called traveledDistance,
        # This distance should made it not start from row1, but from the initialRow of col2 + traveledDistance
        traveledDistance += self.moveArmToRow(initialRowAndIncorrect2[0], row2, -(traveledDistance), incorrect=initialRowAndIncorrect2[1])

        # Move the robot from row1 to row2, adjustment will be the difference between them
        # traveledDistance += self.moveArmToRow(row1, row2, initialRowAndIncorrect1[1] - initialRowAndIncorrect2[1])


        # Drop the object
        self.pickOrDropPiece(pickUp=False)

        # Reset the arm
        robot.turnToStartPosition()

        # Move back to the original position
        if traveledDistance > 0:
            robot.backwardExact(traveledDistance)
        else:
            robot.forwardExact(abs(traveledDistance))

        robot.armRelease()
        time.sleep(2)
        robot.armToStraightPosition()

        # Turn back a bit to adjust the position
        robot.turnExact(-5)

    def moveArmToRow(self, currentRow, row, adjustment, incorrect=0):
        """Method to move the robot arm to a row from current row"""
        distanceToRow = abs(row - currentRow) * \
            CHESSBOARD_SQUARE_LENGTH + adjustment + incorrect
        print("===> DISTANCE TO NEW ROAD: ", distanceToRow)

        forwarded = True

        if distanceToRow < 0:
            # TODO: WRONG LOGIC, SHOULD GO backward
            # If the currentRow has the value smaller than row, go backward to reach to row
            robot.backwardExact(abs(distanceToRow))
            forwarded = False
        else:
            # If the current row has the value larger than row, go forward to reach to row
            robot.forwardExact(distanceToRow)
        # else:
        #     # If the current row is the same with new row, adjust the incorrect by go forward to correct
        #     robot.forwardExact(distanceToRow)

        return distanceToRow

    def pickOrDropPiece(self, pickUp=True):
        """Method to pick up or drop down a piece"""
        # Wait until the robot reach to position
        while robot.isMoving():
            pass
        # Pick up the object
        if pickUp:
            robot.pickUp()
        else:
            robot.dropDown()


if __name__ == '__main__':

    PORT = 9999
    CHESSBOARD_SQUARE_LENGTH = 5

    robot = RobotArm()

    robot.armToStraightPosition()
    robot.turnExact(-5)

    server = socketserver.TCPServer(
        (socket.gethostname(), PORT), RobotArmHandler)
    print(server.server_address)
    server.serve_forever()
