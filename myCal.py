import calendar
import tkinter as tk
from tkinter import ttk
import time
# self.protocol("WM_DELETE_WINDOW", self.close_func)


LABEL_OPTIONS = {'activebackground': 'SystemButtonFace',
                 'activeforeground': 'SystemButtonText',
                 'anchor': 'center',
                 'background': 'SystemButtonFace',
                 'bd': 2,
                 'bg': 'SystemButtonFace',
                 'bitmap': '',
                 'borderwidth': 1,
                 'compound': 'none',
                 'cursor': 'hand2',
                 'disabledforeground': 'SystemDisabledText',
                 'fg': 'SystemButtonText',
                 'font': 'TkDefaultFont',
                 'foreground': 'SystemButtonText',
                 'highlightbackground': 'SystemButtonFace',
                 'highlightcolor': 'SystemWindowFrame',
                 'highlightthickness': 1,
                 'image': '',
                 'justify': 'center',
                 'padx': 4,
                 'pady': 2,
                 'relief': 'raised',      # raised/sunken ridge/groove flat/solid - впуклости\выпуклости
                 'state': 'normal',
                 'takefocus': 0,
                 'text': 'This is a Label',
                 'textvariable': '',
                 'underline': -1,       # letter position (only 1 letter)
                 'width': 10,
                 'height': 10,
                 'wraplength': 30}      # Text width

class CalPopup(tk.Tk):    # Change to Toplevel
    # Locale Settings
    __month_names = ('Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль',
                          'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь')
    __week_names = ('Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс')
    font = ('Lucida', 14, 'bold')  # Times/Verdana/Lucida/Console/Courier/Helvetica   italic
    #font=('Tempus Sans ITC', 12, 'bold')

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

        # ===== EXPEREMENTS =================================

        #self.textF = tk.Text(self, highlightbackground='#F00')
        #self.textF.grid(columnspan=7, sticky='NSEW')
        #self.textF.insert(tk.INSERT, 'xaxaxa')
        tk.Label(self, LABEL_OPTIONS).grid(columnspan=7, )

        # ===================================================

    def buildCal(self, month, year):
        cal_array = calendar.TextCalendar(firstweekday=0).itermonthdays4(int(year), int(month))

        for i, week_day in enumerate(self.__week_names):
            tk.Label(self, text=week_day, width=2, anchor=tk.CENTER).grid(row=1, column=i, ipadx=3, ipady=0)

        row = 2
        for i, di in enumerate(cal_array):
            day_info = {'day': di[2]}
            # Проверка на дни с прошлого\текущего\предыдущего месяца
            if i < 7 and di[2] > 20:
                day_info['month'] = 'prev'
            elif i > 20 and di[2] < 7:
                day_info['month'] = 'next'
            else:
                day_info['month'] = 'current'
            # Holiday
            day_info['Holiday'] = True if di[3] in (5, 6) else False

            current = tk.Label(self, text=di[2], font=self.font, width=2, borderwidth=1, cursor='hand2', takefocus=0,
                               anchor='center',     # n/ne/e/se/s/sw/w/nw/center
                               relief='ridge',      # raised/sunken ridge/groove flat/solid - впуклости\выпуклости
                               state='normal',      # active/normal/disabled
                               background='#DDD', foreground='#111',
                               activebackground='#333', activeforeground='#FFF', disabledforeground='#AAA',
                               highlightcolor='#F00', highlightbackground='#00F', highlightthickness=0)
            current.hidden = day_info      # Vidget parametr
            current.grid(row=row, column=di[3], ipadx=4, ipady=2)

            current.bind('<Enter>', lambda event, bg='#bbb': self.change_bg(event, bg))
            current.bind('<Leave>', lambda event, bg='#ddd': self.change_bg(event, bg))
            # current.bind('<Leave>', lambda event, bg='#ddd': current.config(background=bg)) # works but last
            row = row + 1 if di[3] == 6 else row

    def check_this_button(self, event):
        ww = event.widget
        text = ww['font'] if ww['font'] else ww['text']
        print(text, ww['state'])
        ww.config(state="active")
        print(ww.hidden)
        print('Text', ww.config('text'))

    def change_bg(self, event, bg):     # Like CSS:hover
        event.widget.config(background=bg)

    def doNothing(self):
        print('Nothing to do')
        pass


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
