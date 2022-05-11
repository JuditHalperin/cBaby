import tkinter as tk
from tkinter.ttk import *
from PIL import ImageTk, Image

'''
start window, include explaining about the program and a button to start.
'''

root = tk.Tk()

S="stop"

# start the program
def start():
    print ("start")
    global S
    S = "start"
    root.destroy()


root.configure(background='AliceBlue')
# explaining
msg1 = tk.Label(root,  text="ברוכים הבאים למערכת שינה בטוחה", foreground= 'LightSeaGreen' , font =
               ( 'Lucida Sans Unicode', 20, 'bold'),background='AliceBlue')
msg1.grid(row=1, column=1)

msg2=tk.Label(root, text="המערכת תתריע במקרים הבאים  ", font =
               ( 'Lucida Sans Unicode', 15, ),background='AliceBlue')
msg2.grid(row=2, column=1)

msg3=tk.Label(root, text="אם פני התינוק יהיו מכוסים, אם  התינוק יפרכס ואם צבע הפנים של התינוק ישתנה", font =
( 'Lucida Sans Unicode', 15, ),background='AliceBlue')
msg3.grid(row=3, column=1)

msg4=tk.Label(root, text="לעצירה לחץ על מקש 0 במקלדת", font =
( 'Lucida Sans Unicode', 15, ),background='AliceBlue')
msg4.grid(row=4, column=1)

msg5=tk.Label(root, text="אנא השאר בסביבה הקרובה על מנת שתוכל לשמוע את המערכת", font =
               ( 'Lucida Sans Unicode', 15, 'bold' ),background='AliceBlue')
msg5.grid(row=5, column=1)

# image
img = ImageTk.PhotoImage(Image.open('small baby.png'))
image= tk.Label(root,image = img,background='AliceBlue')
image.grid(row=6,column=1)

# start button, call start function
b1 = tk.Button(root,text="הפעל", command=start ,background="PaleTurquoise", font =
               ( 'Lucida Sans Unicode', 20, 'bold'))
b1.grid(row=7,column=1)

root.mainloop()





