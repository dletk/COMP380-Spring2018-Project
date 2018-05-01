import cv2
import numpy as np

class ChessBoardProcessor:
    """
    Class to create a processor to process the input image from the chessboard.
    This class contains all the method to detect the chess board from video input,
    detect the difference between 2 image of chessboard and infer the last move.
    """

    # =========== CONSTANTS =================
    # TODO: Print a 10x10 board to use as the real chessboard in order to do intensive testing.
    # Keep in mind, 8x8 normal board will result in 6x6 detected board
    BOARD_SIDE_LENGTH = 10
    BOARD_SIDE_INTERNAL = BOARD_SIDE_LENGTH - 1
    SIZE_OF_INTERNAL_CORNERS = (BOARD_SIDE_INTERNAL, BOARD_SIDE_INTERNAL)
    PIECES_NAME = {"K":"King", "Q":"Queen", "R": "Rook", "B" :"Bishop", "N": "Knight", "P": "Pawn"}

    # TODO: CHANGE THE THRESHOLD EVERYTIME SETTING UP THE GAME
    DIFFERENCE_THRESHOLD = 200000
    # The amount is in centimeters
    CHESSBOARD_SQUARE_LENGTH = 5

    def __init__(self, inputSource=0):
        self.videoCap = cv2.VideoCapture(inputSource)
        # The list of corners detected from the chessboard
        self.boardCorners = []
        # This is the raw gray image to use for any internal processing (no dot at each iternal corners)
        self.__rawCurrentBoard = []

        # This currentBoard has a dot at each internal corners for user to check detection accuracy
        self.currentBoard = self.detectChessboard()

        # The list of individual square images. This should be private (not accessed by user)
        self.__currentSquareImages = self.__detectIndividualSquareImages()

        # The variable indicate which side is currently playing, white-0 or black-1
        self.currentPlayingSide = 0

        # ============ Initial setup for a chess board
        # Representation: King K, Queen Q, Rook R, Bishop B, Knight N, Pawn P
        # 0: white side, 1, black side
        # K0: King of White...
        self.pieceAtPosition = {"A1": "R0", "B1": "N0", "C1": "B0", "D1": "Q0", "E1": "K0", "F1": "B0", "G1": "N0", "H1": "R0",
                                "A2": "P0", "B2": "P0", "C2": "P0", "D2": "P0", "E2": "P0", "F2": "P0", "G2": "P0", "H2": "P0",
                                "A8": "R1", "B8": "N1", "C8": "B1", "D8": "Q1", "E8": "K1", "F8": "B1", "G8": "N1", "H8": "R1",
                                "A7": "P1", "B7": "P1", "C7": "P1", "D7": "P1", "E7": "P1", "F7": "P1", "G7": "P1", "H7": "P1",
                                "A3": None, "B3": None, "C3": None, "D3": None, "E3": None, "F3": None, "G3": None, "H3": None,
                                "A4": None, "B4": None, "C4": None, "D4": None, "E4": None, "F4": None, "G4": None, "H4": None,
                                "A5": None, "B5": None, "C5": None, "D5": None, "E5": None, "F5": None, "G5": None, "H5": None,
                                "A6": None, "B6": None, "C6": None, "D6": None, "E6": None, "F6": None, "G6": None, "H6": None}

    def detectChessboard(self):
        """
        Method to initiate the chessboard detection and save the newly detected chessboard
        to the processor's variable
        ATTENTION: Use a blank chessboard for this detection to work best before put the chess pieces on
        """
        readyFlag = input(
            "Please prepare your camera and enter d/D when you are ready \
            \nAttention - Please use a blank board for best detection and put on the pieces after : ")
        while readyFlag not in "dD":
            readyFlag = input("Wrong input, please try again: ")
        self.currentBoard = self.__detect()

    def __detect(self):
        """
        Method to detect the chess board
        This method is private for the purpose of decompse the program
        """

        print("INSTRUCTION: Adjust your chessboard to make sure it fit into the frame and hit d to begin detect.")
        ret, frame = self.videoCap.read()

        while True:
            cv2.imshow("Board", frame)
            keyStroke = chr(cv2.waitKey(1) & 0xff)
            # Use is ready to take picture
            if keyStroke in "dD":
                break
            else:
                ret, frame = self.videoCap.read()

        self.__rawCurrentBoard = frame.copy()

        # Detecting the chessboard can only work on a gray scale image
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Detect the chessboard corner
        # This method find all the internal corners of a chessboard
        # For example, a standard 8x8 chessboard has 7x7 internal corners
        retVal, boardCorners = cv2.findChessboardCorners(gray_image, self.SIZE_OF_INTERNAL_CORNERS, cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
                                                         + cv2.CALIB_CB_FAST_CHECK)
        print("======> Finished findChessboardCorners")
        if retVal:
            print("====> Chess board detected")
            boardCorners = cv2.cornerSubPix(gray_image, boardCorners, (5, 5), (-1, -1),
                                            (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1))

        # Notice: Sometimes the corners will be detected from bottom up, not top down as expected
        # This part of the program chess for this problem and correct the order of corners
        boardCorners = self.__constructTopDownBoardCorners(boardCorners)
        print("=====> Shape: ", boardCorners.shape)

        # Drawout the corners detected for user to chess
        displayed_image = cv2.drawChessboardCorners(
            gray_image, self.SIZE_OF_INTERNAL_CORNERS, boardCorners, retVal)

        # Draw a line between first 2 corners to know where the corners begin
        displayed_image = cv2.line(displayed_image, (boardCorners[0][0][0], boardCorners[0][0][1]), (
            boardCorners[1][0][0], boardCorners[1][0][1]), (0, 0, 255), 2)

        cv2.imshow("Board", displayed_image)
        cv2.waitKey(1000)

        # We only interested in the list of corners, the displayed_image is just for
        # the visualization to check
        self.boardCorners = boardCorners
        return displayed_image

    def __constructTopDownBoardCorners(self, boardCorners):
        """
        Sometimes the corners will be detected from bottom up, not top down as expected
        This method check and correct the corners of
        """
        print("=====> Shape: ", boardCorners.shape)
        x_first_corner = boardCorners[0][0][0]
        x_second_corner = boardCorners[1][0][0]
        y_first_corner = boardCorners[0][0][1]
        y_second_corner = boardCorners[1][0][1]

        # If the board is wrongly detected bottom up, from right to left
        if x_first_corner > x_second_corner:
            # This means the board was detected bottom up
            boardCorners = np.flipud(boardCorners)
            print("=====> FLIPED bottomup")
            return boardCorners
        # Make sure there can be a slightly error of 30 pixels
        elif y_first_corner < y_second_corner - 30:
            # This means the board was detected 90 degree flip to the right.
            newBoardCorners = [[]]
            for row in range(self.BOARD_SIDE_INTERNAL):
                for i in range(self.BOARD_SIDE_INTERNAL - 1, -1, -1):
                    newBoardCorners[0].append(boardCorners[i*self.BOARD_SIDE_INTERNAL+row][0])
            print("=====> FLIPED 90 degrees")
            newBoardCorners = np.asarray(newBoardCorners)
            return newBoardCorners.reshape((self.BOARD_SIDE_INTERNAL * self.BOARD_SIDE_INTERNAL,1,2))
        else:
            return boardCorners

    def __detectIndividualSquareImages(self):
        """
        Method to detect and get the current image of individual squareself.
        This will be used to detect a move later on.
        """
        squareImages = {}

        # THIS IS THE NUMBER OF ROWS AND COLS OF CORNERS, NOT NUMBER OF ROWS AND COLS OF THE BOARD.
        numCols = self.BOARD_SIDE_INTERNAL
        numRows = self.BOARD_SIDE_INTERNAL
        colToNum = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7}
        # Only loop to second last row instead of last row because we need topLeft and botRight position for each square
        for row in range(numRows - 1):
            # TODO: Change this to ABCDEFGH for the actual chessboard
            for col in "ABCDEFGH":
                xTopLeft = int(round(self.boardCorners[numCols * row + colToNum[col]][0][0]))
                yTopLeft = int(round(self.boardCorners[numCols * row + colToNum[col]][0][1]))
                xBotRight = int(round(self.boardCorners[(row+1) * numCols + colToNum[col] + 1][0][0]))
                yBotRight = int(round(self.boardCorners[(row+1) * numCols + colToNum[col] + 1][0][1]))

                # Using numpy array slicing. Because using numpy, y is in front
                square = self.__rawCurrentBoard[yTopLeft:yBotRight, xTopLeft:xBotRight]
                # Map the square to its actual position on the chessboard

                # Attention: The actual row value is numRows - row - 1, because the image is projected from
                # top down, so the first corner is at the top row. Also we want to number from 1, not 0
                squareImages[col+str(numRows - row - 1)] = square
        return squareImages

    def getIndividualSquareImages(self):
        """Method to get the array containing individual square images"""
        return self.__currentSquareImages

    def captureNewBoard(self):
        """Method to capture new board from the video capture"""
        ret, frame = self.videoCap.read()

        if ret:
            self.__rawCurrentBoard = frame.copy()
            # DEBUG: Comment out this part for debug purpose
            # cv2.imshow("Current board", self.__rawCurrentBoard)
            # cv2.waitKey(0)
            return True
        else:
            return False

    def detectMove(self):
        """Method to detect a move on the board"""

        # Get the current chessboard
        self.captureNewBoard()
        # Get the current individual squares image.
        newlyDetectedIndividualSquares = self.__detectIndividualSquareImages()

        # There can only be 2 squares that are differences from a single move
        squaresChanged = []

        for squareCode in newlyDetectedIndividualSquares:
            oldSquare = self.__currentSquareImages[squareCode]
            newSquare = newlyDetectedIndividualSquares[squareCode]
            # Call the method to find the difference
            diff = cv2.absdiff(oldSquare, newSquare)
            diff = diff.sum()
            print(diff)

            # If the sum is different by DIFFERENCE_THRESHOLD, we consider it as difference
            if diff > self.DIFFERENCE_THRESHOLD:
                # print("New Value: ", newValue)
                # print("Old value: ", oldValue)
                squaresChanged.append(squareCode)
                # DEBUG: Use to see the image of detected changed squares
                # cv2.imshow("Old square " + squareCode, oldSquare)
                # cv2.imshow("New square " + squareCode, newSquare)
                # cv2.waitKey(0)

        # DEBUG: Print out the list of squares changed
        print(squaresChanged)

        # After finished finding the differences, assign the newly detected squares to be current squares
        self.__currentSquareImages = newlyDetectedIndividualSquares

        # Return the detected move
        return self.__classifyAndIdentifyMove(squaresChanged)


    def __classifyAndIdentifyMove(self, squaresChanged):
        """Method to classify which kind of move happened on the board."""
        # DEBUG:
        currentPiece1 = self.pieceAtPosition[squaresChanged[0]]
        currentPiece2 = self.pieceAtPosition[squaresChanged[1]]

        if currentPiece1 is None or currentPiece2 is None:
            # This is an empty move, just swap the value
            self.pieceAtPosition[squaresChanged[0]] = currentPiece2
            self.pieceAtPosition[squaresChanged[1]] = currentPiece1
            if currentPiece1 is None:
                return currentPiece2 + " from "+ squaresChanged[1] + " move to " + squaresChanged[0]
            else:
                return currentPiece1 + " from "+ squaresChanged[0] + " move to " + squaresChanged[1]
        else:
            # This is a capture move
            # TODO: Debug the capture move
            # The piece is in the form TypeSide (e.g: K0). Get the side of the piece
            # print(currentPiece1)
            # for char in currentPiece1:
            #     print(char)
            currentPiece1 = currentPiece1.strip()
            currentPiece2 = currentPiece2.strip()

            currentPiece1Side = currentPiece1[1]
            if int(currentPiece1Side) == self.currentPlayingSide:
                # This is the turn of currentPiece1, so it is a capture from piece1 to piece2
                # The last piece1 square become empty, and the position of piece2 is capture by piece1
                self.pieceAtPosition[squaresChanged[0]] = None
                self.pieceAtPosition[squaresChanged[1]] = currentPiece1
                return "Capture of" + currentPiece1Side + " " + currentPiece1 + " capture " + currentPiece2
            else:
                # This is the turn of currentPiece2, so it is a capture from piece2 to piece1
                self.pieceAtPosition[squaresChanged[1]] = None
                self.pieceAtPosition[squaresChanged[0]] = currentPiece2
                return "Capture of" + str(self.currentPlayingSide) + " " + currentPiece2 + " capture " + currentPiece1

    def setCurrentSquareImages(self):
        """Method to set the current square images to the current board setting"""
        self.__currentSquareImages = self.__detectIndividualSquareImages()

    def changeCurrentPlayingSide(self):
        """Method to toggle the current playing side"""
        self.currentPlayingSide = 1 - self.currentPlayingSide

if __name__ == '__main__':
    boardPorcessor = ChessBoardProcessor(inputSource=1)
    # print(boardPorcessor.boardCorners)
    # squares = boardPorcessor.getIndividualSquareImages()
    # print(squares)
    # for key in squares:
    #     print(key)
    #     cv2.imshow(key, squares[key])
    #     cv2.waitKey(0)
    input("Enter to begin: ")
    boardPorcessor.captureNewBoard()
    boardPorcessor.setCurrentSquareImages()
    while True:
        # DEBUG: Work on multiple moves
        input("Enter to move on: ")
        print(boardPorcessor.detectMove())
        boardPorcessor.changeCurrentPlayingSide()
