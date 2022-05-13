
# GUI first page

# Choose "live" or video name such as "video1" or "video2"
MODE = "live"


# import packages
from playsound import playsound
import speech_recognition as sr
from PIL import ImageTk
from tkinter import *
from PIL import Image
import threading
import datetime
import time
import keyboard

# import scripts
import second_page_live
import second_page_video


class FirstPage:

    def __init__(self, root):
        """This function initializes the first page"""

        # root
        self.root = root
        self.root.title("cBaby")
        self.root.geometry("400x400")
        self.root.resizable(False, False)  # disable resizing

        # info page frame
        info_page = Frame(root, bg="white")
        info_page.place(x=0, y=0, height=500, width=500)

        # logo
        logo_frame = Frame(info_page, width=100, height=200)  # create a frame to place the logo on
        logo_frame.place(anchor='se', relx=0.7, rely=0.50)
        logo_image = ImageTk.PhotoImage(Image.open("../data/logo.png"))  # create an ImageTk object
        Label(logo_frame, image=logo_image, background="white").pack()  # create a label widget to display the image

        # text label
        Label(info_page, text=self.__get_text(), font=("Goudy pld style", 18), fg="#619BAF", bg="white").place(x=110, y=270)

        # start button
        self.button = Button(self.root, command=self.start_function, text="Go", bg="#ABCAD5", font=("times new roman", 12))
        self.button.place(x=155, y=330, width=90, height=30)

        # thread to hear the 'go' command in the background
        self.listen = True
        self.query = None
        threading.Thread(target=self.voice, daemon=True).start()

        # threading.Thread(target=self.start_by_key, daemon=True).start()

        # infinite loop waiting for an event to occur and process the event as long as the window is not closed
        root.mainloop()

    def __get_text(self):
        """Top text by current time"""
        dt = datetime.datetime.now()
        if datetime.time(5) <= dt.time() <= datetime.time(12):
            return 'Good Morning!'
        elif datetime.time(12) <= dt.time() <= datetime.time(18):
            return 'Good Afternoon!'
        return 'Good Night!'

    def __take_command(self):
        """listen and recognize words"""
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
            if 'go' in self.query or 'gaon' in self.query:
                self.button.invoke()  # button function without clicking

    """
    def start_by_key(self):
        while self.listen:
            if keyboard.is_pressed('a'):  # start live
                self.button.invoke()  # button function without clicking
            elif keyboard.is_pressed('b'):  # start video
                global MODE
                MODE = "video1"
                self.button.invoke()  # button function without clicking
    """

    def start_function(self):
        """When 'go' is pressed or said, play sound, destroy root and open second page according to MODE"""
        playsound("../data/sound.wav", False)
        time.sleep(1)

        self.listen = False
        self.root.destroy()

        if MODE == "live":
            second_page_live.start()
        else:
            second_page_video.start(MODE)


def main():
    FirstPage(Tk())


if __name__ == '__main__':
    main()
