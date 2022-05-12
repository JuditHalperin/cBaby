
# GUI second page


# import packages
from imutils.video import VideoStream
from PIL import ImageTk, Image
import speech_recognition as sr
from tkinter import messagebox
from twilio.rest import Client
import tkinter as tk
import threading
import datetime
import imutils
import time
import cv2
import PIL


FRAMES_PER_SECOND = 3  # number of frame per a second


class SecondPage:

    def __init__(self, vs):
        """This function initializes the object properties, creates the window, and starts the video loop thread"""

        # classifier to recognize face
        self.faceCascade = cv2.CascadeClassifier("../data/haarcascade_file.xml")
        self.profileFaceCascade = cv2.CascadeClassifier("../data/half_face.xml")

        self.vs = vs  # video stream
        self.thread = None  # video loop thread
        self.stop_event = None  # flag to indicate whether the app is closed
        self.panel = None  # panel to display the frames

        # initialize the tkinter object
        self.root = tk.Tk()
        self.root.title("cBaby")
        self.root.resizable(False, False)  # disable resizing
        self.root.wm_protocol("WM_DELETE_WINDOW", self.on_close)  # set a callback to handle when the window is closed by the X button

        # start the video loop thread
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.video_loop, args=(), daemon=True)
        self.thread.start()

        # top message label
        self.message = tk.Label(self.root, fg="#085768", text=f"Sweet Dreams!", font=('Goudy pld style', 20, 'bold'))
        self.message.pack(side="top", expand="yes", padx=10, pady=10)

        # stop button
        self.button = tk.Button(self.root, text="Bye", command=self.on_close, bg="#ABCAD5", font=("times new roman", 12))
        self.button.pack(side="bottom", expand="yes", padx=10, pady=10)

        # Start a thread to hear the 'bye' command in the background
        self.listen = True
        self.query = None
        threading.Thread(target=self.voice, daemon=True).start()

        # variables
        self.TWO_MINS = 0
        self.DELTA = 0
        self.HALF_MIN = 0
        self.MIN = 0
        self.ALARM_ON = False  # boolean variable indicating whether the alarm is on or off

    # The function get 2 frames, and check if there is a significant moving for 2 minutes.
    def moving(self, frame1, frame2):

        WIDTH = frame1.shape[0]
        LENGTH = frame1.shape[1]

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
        sum = sum/(WIDTH * LENGTH)
        if self.TWO_MINS > 0:  # if we started to count 2 mins
            if self.TWO_MINS == 120:  # after 2 mins
                if self.DELTA >= 120 * 20:  # if there was a significant moving- send a message
                    self.alarm("baby is having a seizure")
                    self.TWO_MINS = 0
                    self.DELTA = 0
                else:
                    self.TWO_MINS = 0  # else- we didnt find significant of moving, restart the counters
                    self.DELTA = 0
            elif sum > 20:  # if sum>20- add 1 to 2 mins and add sum to delta
                self.TWO_MINS += 1
                self.DELTA += sum
            else:  # else- we didnt find a significant moving, restart the counters
                self.TWO_MINS = 0
                self.DELTA = 0
        elif sum > 20:  # if we didnt start to count 2 mins, and sum>20- start count 2 mins and add sum to delta
            self.TWO_MINS += 1
            self.DELTA += sum

    # Get a frame, convert to grayscales and find face in the frame.
    def face_in_image(self, frame):
        # convert to grayscales
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        img = cv2.GaussianBlur(img, (21, 21), 0)
        # find face in img
        faces = self.faceCascade.detectMultiScale(
            img,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        profile_faces = self.profileFaceCascade.detectMultiScale(
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
    def face_recognition(self, frame):

        face, len_faces, len_profile_faces = self.face_in_image(frame)   # call face_in-image function

        if self.HALF_MIN > 0:  # if we started to count 0.5 min
            if self.HALF_MIN == 10:  # after 0.5 min
                if len_faces == 0 and len_profile_faces == 0:  # if there is no face in the img- send a message
                    self.alarm("blanket over baby's face")
                    self.HALF_MIN = 0
                else:
                    self.HALF_MIN = 0  # else- we find face, restart the counter
            elif len_faces == 0 and len_profile_faces == 0:  # if there is no face in the img, add 1 to half_min
                self.HALF_MIN += 1
            else:  # else- we find face, restart the counter
                self.HALF_MIN = 0
        elif len_faces == 0 and len_profile_faces == 0:
            # if we didn't start to count and there is no face in the img- start counting 0.5 min.
            self.HALF_MIN += 1

    # get the first frame in the video and return the mean color of the face
    def color_frame1(self, frame):
        face, len_faces, len_profile_faces = self.face_in_image(frame)   # call face_in-image function
        if len_faces > 0 or len_profile_faces > 0:  # if there is face in image- return the color
            color = face.mean()
            return color
        # if there is no face in image- please change the camera place
        return None

    # get a frame and the color of the face in the first frame,
    # and check if there is a significant different in the face color for 1 minute.
    def color_recognition(self, frame, first_color):

        face, len_faces, len_profile_faces = self.face_in_image(frame)   # call face_in-image function
        if len_faces > 0 or len_profile_faces > 0:  # if there is face in image
            color = face.mean() # get the mean color of the face
            # print('MIN', MIN)
            if self.MIN > 0:  # if we started to count 1 min
                if self.MIN == 60:  # after 1 min
                    if abs(color - first_color) > 5:  # if there is different in the face color- send a message
                        self.alarm("baby's face color changed")
                        self.MIN = 0
                    else:
                        self.MIN = 0  # else- there is no different
                elif abs(color - first_color) > 5:  # if there is different in the face color, during the min.
                    self.MIN += 1    # add 1 to min
                else:  # else- there is no different, restart the counter
                    self.MIN = 0
            elif abs(color - first_color) > 5:  # if there is different in the face color and min=0, start to count 1 min
                self.MIN += 1

    def video_loop(self):
        """This function loops over the video stream"""

        last_frame_time = datetime.datetime.now()  # last time a frame was analyzed

        first_frame = None
        last_frame = None
        first_color = None

        while not self.stop_event.is_set():  # while the app is not closed

            current_frame = self.vs.read()  # grab the frame from the threaded video file stream
            current_frame = imutils.resize(current_frame, width=450)  # resize the frame
            current_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB)  # convert from BGR (cv2 format) to RGB (tkinter format)

            if first_frame is None:
                first_frame = current_frame
                last_frame = current_frame
                first_color = self.color_frame1(first_frame)  # save the mean color of the face in the first frame
                if first_color is None:
                    first_frame = None
                    #messagebox.showerror("Error", "No face detected.", parent=self.root)
                    continue

            # see if a sufficient time passed since the previous frame was analysed
            if not self.ALARM_ON and datetime.datetime.now() - last_frame_time >= datetime.timedelta(seconds=1/FRAMES_PER_SECOND):

                self.moving(last_frame, current_frame)  # moving recognition
                self.face_recognition(current_frame)    # face recognition
                self.color_recognition(current_frame, first_color)  # change color recognition

                last_frame_time = datetime.datetime.now()  # update the last time a frame was analyzed

            last_frame = current_frame

            cv2.putText(current_frame, str(self.show_time()), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)  # draw the time on the frame

            current_frame = PIL.Image.fromarray(current_frame, mode="RGB")  # turn the array into an image, with mode RGB
            current_frame = ImageTk.PhotoImage(current_frame)  # return an image to display

            if self.panel is None:  # initialize the panel and show the frame
                self.panel = tk.Label(image=current_frame)
                self.panel.image = current_frame
                self.panel.pack(side="left", padx=10, pady=10)

            else:  # update the panel to show the frame
                self.panel.configure(image=current_frame)
                self.panel.image = current_frame

    def __take_command(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            audio = r.listen(source)
        print("Recognizing...")
        try:
            self.query = r.recognize_google(audio, language='en-in')
            print(f"User said: {self.query}\n")
            return self.query
        except Exception:
            return ""

    def voice(self):
        while self.listen:
            self.query = self.__take_command().lower()
            if 'bye' in self.query or 'by' in self.query or 'buy' in self.query:
                self.button.invoke()  # button function without clicking

    def show_alert(self, text):
        """This function shows the alert message for a few seconds"""
        self.message['text'] = "Alert: " + text  # update the label to show the alert with the optional text
        self.message['fg'] = "red"  # change to alert color

    def show_time(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # get a message and call alarm_window
    def alarm(self, message):
        self.ALARM_ON = True  # turn the alarm on

        # alert text
        threading.Thread(target=self.show_alert, args=(message,), daemon=True).start()  # start a thread to show the alert text for a few seconds in the background

        # call and send message
        from_number = "+13253356913"
        to_number = "+972586468596"
        client = Client("AC199fd330375e3b283e002502ab97145f", "2ff7f7222684bf3db26f90258727ca0f")
        client.calls.create(to=to_number, from_=from_number, url="http://havanat.net/naama/test.xml", method="GET")
        client.messages.create(to=to_number, from_=from_number, body="cBaby warning message: " + message)

    def on_close(self):
        """This function stops the video stream and the root when either the stop or the X button is pressed"""
        if self.thread.is_alive():
            self.stop_event.set()
            self.vs.stop()
        self.root.destroy()


def start():
    """This function starts the video stream and the loop"""

    vs = VideoStream(src=1).start()  # start the video stream thread, 0 indicates index of webcam on system
    time.sleep(5.0)  # pause for 5 seconds to allow the camera sensor to warm up

    dd = SecondPage(vs)  # start the loop
    dd.root.mainloop()  # infinite loop waiting for an event to occur and process the event as long as the window is not closed
