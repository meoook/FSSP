import tkinter as tk


class Gui:

    def __init__(self, master):
        frame = tk.Frame(master)
        frame.pack()

        self.btn_tt = tk.Button(frame, text='This blank Button', command=self.msg)
        self.btn_tt.pack(side=tk.LEFT)

        self.btn_quit = tk.Button(frame, text='Quit', command=frame.quit)
        self.btn_quit.pack(side=tk.LEFT)

    def msg(self):
        print('Test')


root = tk.Tk()
b = Gui(root)
root.mainloop()