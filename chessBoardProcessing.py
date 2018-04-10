import cv2


class ChessBoardProcessor():
    """
    Class to create a processor to process the input image from the chessboard.
    This class contains all the method to detect the chess board from video input,
    detect the difference between 2 image of chessboard and infer the last move.
    """

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
        # The list of newly detected square images, used to compare with the current value
        # to detect a move
        self.__newlyDetectedSquareImages = []

    def detectChessboard(self):
        """
        Method to initiate the chessboard detection and save the newly detected chessboard
        to the processor's variable
        """
        readyFlag = input(
            "Please prepare your camera and enter d/D when you are ready: ")
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

        # Detecting the chessboard can only work on a gray scale image
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.__rawCurrentBoard = gray_image.copy()
        # Detect the chessboard corner
        # This method find all the internal corners of a chessboard
        # For example, a standard 8x8 chessboard has 7x7 internal corners
        retVal, boardCorners = cv2.findChessboardCorners(gray_image, (7, 7), cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
                                                         + cv2.CALIB_CB_FAST_CHECK)
        print("======> Finished findChessboardCorners")
        if retVal:
            print("====> Chess board detected")
            boardCorners = cv2.cornerSubPix(gray_image, boardCorners, (5, 5), (-1, -1),
                                            (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1))
        # Drawout the corners detected for user to chess
        displayed_image = cv2.drawChessboardCorners(
            gray_image, (7, 7), boardCorners, retVal)

        # Draw a line between first 2 corners to know where the corners begin
        displayed_image = cv2.line(displayed_image, (boardCorners[0][0][0], boardCorners[0][0][1]), (
            boardCorners[1][0][0], boardCorners[1][0][1]), (0, 0, 255), 2)

        cv2.imshow("Board", displayed_image)
        cv2.waitKey(1000)

        # We only interested in the list of corners, the displayed_image is just for
        # the visualization to check
        self.boardCorners = boardCorners
        return displayed_image

    def __detectIndividualSquareImages(self):
        """
        Method to detect and get the current image of individual squareself.
        This will be used to detect a move later on.
        """
        squareImages = {}

        # THIS IS THE NUMBER OF ROWS AND COLS OF CORNERS, NOT NUMBER OF ROWS AND COLS OF THE BOARD.
        numCols = 7
        numRows = 7
        colToNum = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7}
        # Only loop to second last row instead of last row because we need topLeft and botRight position for each square
        for row in range(0, numRows-1):
            for col in "ABCDEF":
                # Make sure the last dot at each row does not count
                if colToNum[col] < numCols - 1:
                    xTopLeft = int(round(self.boardCorners[numRows * row + colToNum[col]][0][0]))
                    yTopLeft = int(round(self.boardCorners[numRows * row + colToNum[col]][0][1]))
                    xBotRight = int(round(self.boardCorners[(row+1) * numRows + colToNum[col] + 1][0][0]))
                    yBotRight = int(round(self.boardCorners[(row+1) * numRows + colToNum[col] + 1][0][1]))

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

    def getNewlyDetectedSquareImages(self):
        """Method to get the array containing newly detected individual square images"""

if __name__ == '__main__':
    boardPorcessor = ChessBoardProcessor()
    print(boardPorcessor.boardCorners)
    squares = boardPorcessor.getIndividualSquareImages()
    print(squares)
    for key in squares:
        print(key)
        cv2.imshow(key, squares[key])
        cv2.waitKey(0)
