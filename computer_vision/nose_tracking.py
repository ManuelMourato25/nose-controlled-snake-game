from cv2 import cv2
import dlib
import numpy as np
from messaging.rabbitmq import receive, create_queue
import os
import sys

def shape_to_np(shape, dtype="int"):
    """
    Convert landmarks to coordinates array
    :param shape: landmarks
    :param dtype: array type
    :return:
    """
    # initialize the list of (x, y)-coordinates
    coords = np.zeros((68, 2), dtype=dtype)
    # loop over the 68 facial landmarks and convert them
    # to a 2-tuple of (x, y)-coordinates
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    # return the list of (x, y)-coordinates
    return coords


def nose_on_mask(mask, side, shape):
    """
    Return mask that gets the nose shape
    :param mask:
    :param side:
    :param shape:
    :return:
    """
    points = [shape[i] for i in side]
    points = np.array(points, dtype=np.int32)
    mask = cv2.fillConvexPoly(mask, points, 255)
    return mask


def contouring(thresh, img):
    """

    :param thresh: threshold to consider during contouring
    :param img: image
    :return:
    """
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    try:
        cnt = max(contours, key=cv2.contourArea)
        cv2.drawContours(img, cnt, -1, (0, 255, 0), 3)
        moments = cv2.moments(cnt)
        cx = int(moments['m10'] / moments['m00'])
        cy = int(moments['m01'] / moments['m00'])
        return cx, cy
    except:
        return None, None


def detect_nose():
    """
    Function to detect noses in each video frame
    :return:
    """
    # Function to detect a face in a picture or video
    detector = dlib.get_frontal_face_detector()

    # Predictor for face features (eyes, mouth, nose,etc). Takes a pretrained classifier as input
    os.chdir(sys.path[0])
    predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

    # Points from the 68 landmarks that make up the nose
    nose = [27, 28, 29, 30, 31, 32, 33, 34, 35]

    # Start video capturing
    cap = cv2.VideoCapture(0)
    # Get the first image frame
    ret, img = cap.read()

    # Copy the first image frame
    thresh = img.copy()

    #  creates a window that can be used as a placeholder for images and trackbars
    cv2.namedWindow('image')

    kernel = np.ones((9, 9), np.uint8)

    # Create queue to send and receive commands to the pygame
    connection, channel = create_queue(host='localhost', queue='snake_game')

    def nothing(x):
        pass

    # Create trackbar, applied to the named window defined above, that goes from 0 to 255
    cv2.createTrackbar('threshold', 'image', 0, 255, nothing)

    last_nose_center_x = None
    current_nose_center_x = None
    last_nose_center_y = None
    current_nose_center_y = None
    start_game = False
    while True:
        # Get next frame in image
        ret, img = cap.read()
        # Convert image from bgr to gray color space
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Gets the rectangles that identify faces in the image
        rects = detector(gray, 1)
        # For each face rectangle found
        for rect in rects:
            # Get all 68 face landmarks
            shape = predictor(gray, rect)
            # Convert landmark points to a list of coordinates
            shape = shape_to_np(shape)
            # Initialize a numpy array
            mask = np.zeros(img.shape[:2], dtype=np.uint8)
            # Insert into the array only the landmarks that correspond to the nose
            mask = nose_on_mask(mask, nose, shape)

            # Convolution of eye pixels with kernel
            mask = cv2.dilate(mask, kernel, 5)
            # Positions of eye points in the image will be transformed
            my_nose = cv2.bitwise_and(img, img, mask=mask)

            # Get mask of points in image which is not the nose
            mask = (my_nose == [0, 0, 0]).all(axis=2)
            # All image points where there are not eyes will be black
            my_nose[mask] = [255, 255, 255]
            # Convert noses in image to gray
            nose_gray = cv2.cvtColor(my_nose, cv2.COLOR_BGR2GRAY)
            # Get current position of the trackbar
            threshold = cv2.getTrackbarPos('threshold', 'image')

            # For the nose pixels, if a pixel is bellow the threshold, it becomes black
            _, thresh = cv2.threshold(nose_gray, threshold, 255, cv2.THRESH_BINARY)

            thresh = cv2.erode(thresh, None, iterations=2)  # 1
            thresh = cv2.dilate(thresh, None, iterations=4)  # 2
            thresh = cv2.medianBlur(thresh, 3)  # 3
            thresh = cv2.bitwise_not(thresh)
            # Create red circle around the eyes based on the threshold
            current_nose_center_x, current_nose_center_y = contouring(thresh, img)

        # Check if position changed relative to last frame
        # The value of 20 was established as the amount of pixel difference between
        # frames, for meaningful movement
        # Based on relative change, send event to pygame
        if start_game is not True:
            command = receive(channel, 'snake_game')
            if not isinstance(command, str):
                command = command.decode("utf-8")
            if command == 'START':
                start_game = True
        if start_game:
            command = 'NOTHING'
            if (last_nose_center_x is not None) and (
                    last_nose_center_y is not None) \
                    and (current_nose_center_x is not None) and (
                    current_nose_center_y is not None):
                if current_nose_center_x - last_nose_center_x > 20:
                    command = "LEFT"
                if current_nose_center_x - last_nose_center_x < -20:
                    command = "RIGHT"
                if current_nose_center_y - last_nose_center_y > 20:
                    command = "DOWN"
                if current_nose_center_y - last_nose_center_y < -20:
                    command = "UP"

            # Send movement to snake game
            if command in ["RIGHT", "LEFT", "UP", "DOWN"]:
                channel.basic_publish(exchange='', routing_key='snake_game', body=command)
                print(" Sent command: " + command)

            last_nose_center_x = current_nose_center_x
            last_nose_center_y = current_nose_center_y

        # show the image with the face detections + facial landmarks
        cv2.imshow('nose', img)
        cv2.imshow("image", thresh)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            channel.queue_delete(queue='snake_game')
            break
    # Destroy windows and close camera
    connection.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    detect_nose()
