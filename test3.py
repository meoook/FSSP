import tkinter as tk
from tkinter import ttk

from tkcalendar import DateEntry

root = tk.Tk()
cal = DateEntry(root, width=11, background='darkblue',
                foreground='white', borderwidth=2, locale='ru_RU', font="Arial 24")
cal.pack(padx=10, pady=10)
root.mainloop()
