import cv2


def getChessboard():
    """Detect the chess board"""
    videoCap = cv2.VideoCapture(0)
    ret, frame = videoCap.read()

    while True:
        cv2.imshow("Board", frame)
        keyStroke = chr(cv2.waitKey(1) & 0xff)
        # Use is ready to take picture
        if keyStroke in "dD":
            break
        else:
            ret, frame = videoCap.read()

    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    retVal, boardCorners = cv2.findChessboardCorners(gray_image, (7, 7), cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
                                                     + cv2.CALIB_CB_FAST_CHECK)
    print("======> Finished findChessboardCorners")
    print(boardCorners.shape)

    if retVal:
        print("====> Chess board detected")
        boardCorners = cv2.cornerSubPix(gray_image, boardCorners, (5, 5), (-1, -1),
                                        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1))
    result_image = cv2.drawChessboardCorners(
        gray_image, (7, 7), boardCorners, retVal)

    print(boardCorners.shape)
    result_image = cv2.line(result_image, (boardCorners[0][0][0], boardCorners[0][0][1]), (boardCorners[1][0][0], boardCorners[1][0][1]), (0,0,255), 2)

    return result_image


cv2.imshow("Board", getChessboard())
cv2.waitKey(0)
