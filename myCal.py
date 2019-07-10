import calendar
import tkinter as tk
from tkinter import ttk
import time
# self.protocol("WM_DELETE_WINDOW", self.close_func)


class CalPopup(tk.Tk):    # Change to Toplevel
    # Locale Settings
    __month_names = ('Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль',
                          'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь')
    __week_names = ('Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс')

    def __init__(self):
        super().__init__()
        self.title('Календарь етить')
        # self.update()
        # self.winfo_height()
        self.geometry('+500+400')
        self.resizable(False, False)
        self.overrideredirect(1)
        self.bind('<Button-1>', self.check_this_button)
        self.bind('<FocusOut>', lambda event: self.destroy())  # <Motion>
        # Today
        self.selected = time.strftime("%d.%m.%Y", time.localtime()).split('.')
        self.buildCal(self.selected[1], self.selected[2])

    def buildCal(self, month, year):
        cal_array = calendar.TextCalendar(firstweekday=0).itermonthdays4(int(year), int(month))

        for i, week_day in enumerate(self.__week_names):
            tk.Label(self, text=week_day, width=2, anchor=tk.CENTER).grid(row=1, column=i, ipadx=3, ipady=0)

        row = 2
        for a in cal_array:
            column = a[3]
            current = tk.Label(self, text=a[2], relief=tk.RIDGE, width=2, anchor=tk.CENTER,  # style="C.TLabel",
                               background='#DDD', foreground='#111', activebackground='#333', activeforeground='#FFF',
                               disabledforeground='#AAA',
                               highlightcolor='#F00', highlightbackground='#00F', highlightthickness=0,
                               font=('Courier', 14),  # , 'italic'), # Lucida Console
                               state='normal',  # active/normal/disabled
                               borderwidth=1, cursor='hand2', takefocus=0)
            current.grid(row=row, column=column, ipadx=4, ipady=2)  # SUNKEN/RIDGE/FLAT
            current.bind('<Enter>', self.mouse_on)
            current.bind('<Leave>', self.mouse_off)
            # current.bind('<Leave>', lambda event, bg='#ddd': current.config(background=bg)) # works but last

            row = row + 1 if column == 6 else row

    def check_this_button(self, event):
        ww = event.widget
        text = ww['text'] if ww['text'] else 'tt'
        print(text, ww['state'])
        ww.config(state="active")

    def mouse_on(self, event):
        event.widget.config(background='#BBB')

    def mouse_off(self, event):
        event.widget.config(background='#DDD')


gui = CalPopup()
gui.mainloop()
'''
# custom ttk styles
style = ttk.Style()
arrow_layout = lambda direrction: ([('Button.focus', {'children': [('Button.%sarrow' % direrction, None)]})])
style.layout('L.TButton', arrow_layout('left'))
style.layout('R.TButton', arrow_layout('right'))

lbtn = ttk.Label(cal_frame, style='L.TButton').grid(row=0, column=0)
rbtn = ttk.Label(cal_frame, style='R.TButton').grid(row=0, column=3)
'''
