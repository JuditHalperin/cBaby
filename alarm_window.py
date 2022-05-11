import tkinter as tk
from tkinter.ttk import *
from PIL import ImageTk, Image
from playsound import playsound

'''
alarm window, open when the baby is in danger. show a message and play an alarm.
'''


# play alarm
def sound():
    playsound("Ring.wav", False)


# stop the program
def stop():
    exit(1)

def window(msg):
    root = tk.Tk()

    root.configure(background='AliceBlue')
    # call sound function
    root.after(100, sound)

    # show message
    msg1 = tk.Label(root, text=msg ,foreground= 'red' , font =
               ( 'Lucida Sans Unicode', 20, 'bold'),background='AliceBlue')
    msg1.grid(row=1, column=1)

    # image
    img = ImageTk.PhotoImage(Image.open('crying.png'))
    image = tk.Label(root, image=img, background='AliceBlue')
    image.grid(row=2, column=1)

    # stop button. call stop function
    b1 = tk.Button(root, text="סגירה", command=stop, background="PaleTurquoise", font =
               ( 'Lucida Sans Unicode', 20, 'bold'))
    b1.grid(row=3, column=1)

    root.mainloop()
