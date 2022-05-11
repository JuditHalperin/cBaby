import cv2
import time
import user_window
import alarm_window

'''
This file is not a part of the project! 
Our program works in real time (live file), but we used this file to train and try our code on pre-recorded videos.
'''


# global variables
TWO_MINS = 0
DELTA = 0
HALF_MIN = 0
MIN = 0
WIDTH= 0
LENGTH= 0

# classifier to recognize face
faceCascade = cv2.CascadeClassifier("haarcascade_file.xml")
profileFaceCascade = cv2.CascadeClassifier("half_face.xml")


# The function get 2 frames, and check if there is a significant moving for 2 minutes.
def moving(frame1, frame2):
    # global variables
    global TWO_MINS
    global DELTA
    global WIDTH
    global LENGTH

    # convert frame1 and frame2 to grayscales.
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray1 = cv2.GaussianBlur(gray1, (21, 21), 0)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.GaussianBlur(gray2, (21, 21), 0)

    # find the different between frame1 and frame2
    deltaframe = cv2.absdiff(gray1, gray2)
    threshold = cv2.threshold(deltaframe, 25, 255, cv2.THRESH_BINARY)[1]
    threshold = cv2.dilate(threshold, None)
    # sum the threshold
    sum = 0
    for i in threshold:
        for j in i:
            sum += j

    # print ("2 mins", TWO_MINS)

    # normalization of the sum, according to the frames' size.
    sum = sum/(WIDTH*LENGTH)
    # print('sum',sum)
    if TWO_MINS > 0:  # if we started to count 2 mins
        if TWO_MINS == 120:  # after 2 mins
            if DELTA >= 120 * 20:  # if there was a significant moving- send a message
                alarm("תנועה מרובה. התינוק התעורר או מפרכס")
                TWO_MINS = 0
                DELTA = 0
            else:
                TWO_MINS = 0  # else- we didnt find significant of moving, restart the counters
                DELTA = 0
        elif sum > 20:  # if sum>20- add 1 to 2 mins and add sum to delta
            TWO_MINS += 1
            DELTA += sum
        else:  # else- we didnt find a significant moving, restart the counters
            TWO_MINS = 0
            DELTA = 0
    elif sum > 20:  # if we didnt start to count 2 mins, and sum>20- start count 2 mins and add sum to delta
        TWO_MINS += 1
        DELTA += sum


# Get a frame, convert to grayscales and find face in the frame.
def face_in_image(frame):
    # convert to grayscales
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    img = cv2.GaussianBlur(img, (21, 21), 0)
    # find face in img
    faces = faceCascade.detectMultiScale(
        img,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    profile_faces = profileFaceCascade.detectMultiScale(
        img,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    face=[]
    if len(faces) > 0:  # if there is face in the image
        for (x, y, w, h) in faces:
            face = frame[x:x + w, y: y + h] # add the face pixels to face
    elif len(profile_faces) > 0:    # if there is profile face in the image
        for (x, y, w, h) in profile_faces:
            face = frame[x:x + w, y: y + h] # add the face pixels to face

    return face, len(faces), len(profile_faces) # return face, and how many faces were found.


# get a frame, and and check if there wasn't face in the frames for 0.5 minute.
def face_recognition(frame):
    # global variable
    global HALF_MIN

    face, len_faces, len_profile_faces = face_in_image(frame)   # call face_in-image function

    if HALF_MIN > 0:  # if we started to count 0.5 min
        if HALF_MIN == 30:  # after 0.5 min
            if len_faces == 0 and len_profile_faces == 0:  # if there is no face in the img- send a message
                alarm("פנים מכוסות")
                HALF_MIN = 0
            else:
                HALF_MIN = 0  # else- we find face, restart the counter
        elif len_faces == 0 and len_profile_faces == 0:  # if there is no face in the img, add 1 to half_min
            HALF_MIN += 1
        else:  # else- we find face, restart the counter
            HALF_MIN = 0
    elif len_faces == 0 and len_profile_faces == 0:
        # if we didn't start to count and there is no face in the img- start counting 0.5 min.
        HALF_MIN += 1


# get the first frame in the video and return the mean color of the face
def color_frame1(frame):
    face, len_faces, len_profile_faces = face_in_image(frame)   # call face_in-image function
    if len_faces > 0 or len_profile_faces > 0:  # if there is face in image- return the color
        color = face.mean()
        return color
    else:   # if there is no face in image- please change the camera place
        alarm(" מקם את המצלמה מחדש, כך שפני התינוק יהיו בכיוון ישר למצלמה")
        exit(1)


# get a frame and the color of the face in the first frame,
# and check if there is a significant different in the face color for 1 minute.
def color_recognition(frame, first_color):
    global MIN
    face, len_faces, len_profile_faces = face_in_image(frame)   # call face_in-image function
    if len_faces > 0 or len_profile_faces > 0:  # if there is face in image
        color = face.mean() # get the mean color of the face
        # print('MIN', MIN)
        if MIN > 0:  # if we started to count 1 min
            if MIN == 60:  # after 1 min
                if abs(color - first_color) > 5:  # if there is different in the face color- send a message
                    alarm("זוהה שינוי בצבע הפנים")
                    MIN = 0
                else:
                    MIN = 0  # else- there is no different
            elif abs(color - first_color) > 5:  # if there is different in the face color, during the min.
                MIN += 1    # add 1 to min
            else:  # else- there is no different, restart the counter
                MIN = 0
        elif abs(color - first_color) > 5:  # if there is different in the face color and min=0, start to count 1 min
            MIN += 1


# get a message and call alarm_window
def alarm(msg):
    alarm_window.window(msg)


# play the video and call the other functions to recognize signs of distress in the baby
def mainFunc():
    global WIDTH
    global LENGTH

    cap = cv2.VideoCapture("face1.mp4") # open the video

    frame1 = cap.read() #read the first frame
    frame1 = frame1[1]
    first_color=color_frame1(frame1)    # save the mean color of the face in the first frame
    WIDTH = cap.get(3) # save width and length of the frame
    LENGTH = cap.get(4)

    while not cap.isOpened():   # if there is a problem in playing the video
        cap = cv2.VideoCapture("face1.mp4")
        cv2.waitKey(1000)
        print("Wait for the header")

    pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
    while True:
        start_time = time.time()
        flag, frame2 = cap.read()   # read the current frame

        if flag:

            moving(frame1, frame2)  # moving recognition
            face_recognition(frame2)  # face recognition
            color_recognition(frame2, first_color)  # change color recognition

            # The frame is ready and already captured
            cv2.imshow('video', frame2) # show the window
            pos_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            print(str(pos_frame) + " frames")
            time.sleep(1.0 - time.time() + start_time)  # Sleep for 1 second minus elapsed time
            frame2 = frame1
        else:
            # The next frame is not ready, so we try to read it again
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos_frame - 1)
            print("frame is not ready")
            # It is better to wait for a while for the next frame to be ready
            cv2.waitKey(1000)

        if cv2.waitKey(1) == ord('0'):  # close the program
            break
        # If the number of captured frames is equal to the total number of frames- stop.
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            break


if user_window.S == "start":
    mainFunc()
