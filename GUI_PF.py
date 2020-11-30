import tkinter as tk
from tkinter import PhotoImage
import ctypes
import DefCamPF as DC
import DefUpdPF as DU
from shutil import rmtree
# setting root window:

root = tk.Tk()
root.title("Proyecto Final 202030-08 Uninorte")
#root.config(bg="#100e17")
root.config(bg="black")
root.geometry("268x618+0+5")

# load round corner button image:

#img0 = PhotoImage(file=r"btn1.png")
img1 = PhotoImage(file=r"LogoIS.png")

'''def Upgrade():
	DU.EjecutarUpd()
	ctypes.windll.user32.MessageBoxW(0, "La informacion ha sido obtenido de la base de datos", "DB", 1)'''

def FaceRecgn():
	ctypes.windll.user32.MessageBoxW(0, "Se procede a activar el software", "Execute", 1)
	DC.EjecutarCam()

# Button & Label widgets:

label = tk.Label(text="Uninorte PF 202030-08 ", font="Bahnschrift 14", bg="#ff1a00", fg="white", borderwidth=15, relief=tk.RAISED, cursor="hand2").place(x=24, y=200)

#tk.Button(root, image=img0, bg="#100e17", activebackground="#100e17", relief=tk.RAISED, borderwidth=0, padx=0, pady=40, cursor="hand2", width=100, command = Upgrade).place(x=200, y=180)

tk.Button(root, image=img1, bg="#100e17", activebackground="#100e17", relief=tk.RAISED, borderwidth=10, padx=0, pady=40, cursor="hand2", width=150, command = FaceRecgn).place(x=54, y=300)

# window in mainloop:
root.mainloop()

