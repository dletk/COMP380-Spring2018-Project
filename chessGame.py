from chessBoardProcessing import *
from client import *

# Creat the chessboard processor
boardPorcessor = ChessBoardProcessor(inputSource=1)

# Before hit enter, set up the board
input("Hit enter to begin the game: ")

boardPorcessor.captureNewBoard()
boardPorcessor.setCurrentSquareImages()

while True:
    # This is the turn of the player
    input("Enter to move on: ")
    print(boardPorcessor.detectMove())
    boardPorcessor.changeCurrentPlayingSide()

    # This is the turn of the robot
    # At this step, use the AI agent to calculate the next move, here we are just hardcode
    # Move the piece from A7 to D4
    move = input("Enter your move: ")
    move = move.strip()

    # Create connection to robot
    socket = ClientSideRobotArm()
    socket.sendData(move)
    while socket.receivedData != "done":
        pass
    print("Complete move")
    print(boardPorcessor.detectMove())
