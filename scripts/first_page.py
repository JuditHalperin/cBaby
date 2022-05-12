
# GUI first page


MODE = "video1"  # "live" or video name


# import packages
import threading
from tkinter import *
from PIL import ImageTk
from PIL import Image
import speech_recognition as sr
import datetime

# import script
import second_page
import second_page_video


LISTENNING = True


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
        Label(info_page, text=self.get_text(), font=("Goudy pld style", 18), fg="#619BAF", bg="white").place(x=110, y=270)

        # start button
        Button(self.root, command=self.start_function, text="Go", bg="#ABCAD5", font=("times new roman", 12)).place(x=155, y=330, width=90, height=30)

        # Start a thread to hear the 'go' command in the background
        threading.Thread(target=self.voice, daemon=True).start()

        # infinite loop waiting for an event to occur and process the event as long as the window is not closed
        root.mainloop()

    def get_text(self):
        dt = datetime.datetime.now()
        # dt = datetime.datetime(2014, 2, 10, 2, 39, 30, 768979)
        if datetime.time(5) <= dt.time() <= datetime.time(12):
            return 'Good Morning!'
        elif datetime.time(12) <= dt.time() <= datetime.time(18):
            return 'Good Afternoon!'
        return 'Good Night!'

    def __take_command(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            #r.pause_threshold = 1
            audio = r.listen(source)
        return r.recognize_google(audio, language='en-in')

    def voice(self):
        global LISTENNING
        while LISTENNING:
            query = self.__take_command().lower()
            if 'go' in query:
                #print(query)
                #print('heard go')
                self.start_function()

    def start_function(self):
        global LISTENNING
        LISTENNING = False
        self.root.destroy()

        if MODE == "live":
            second_page.start()
        else:
            second_page_video.start(MODE)


def main():
    FirstPage(Tk())


if __name__ == '__main__':
    main()
