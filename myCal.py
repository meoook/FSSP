import calendar
import tkinter as tk
from tkinter import ttk
import time
# self.protocol("WM_DELETE_WINDOW", self.close_func)
#for child in infoFrame.winfo_children():
#    child.destroy()

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
                 'highlightthickness': 2,
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
                 'width': 25,
                 'height': 4,
                 'wraplength': 120}      # Text width


class CalPopup(tk.Tk):    # Change to Toplevel
    # Locale Settings
    __month_names = ('Zero Count', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль',
                          'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь')
    __week_names = ('Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс')
    font_size = 14
    font = ('Lucida', font_size, 'bold')  # Times/Verdana/Lucida/Console/Courier/Helvetica   italic
    week_font = ('Console', int(font_size//1.5))
    #font=('Tempus Sans ITC', 12, 'bold')

    def __init__(self):
        super().__init__()
        self.title('Календарь етить')
        # self.update()
        # self.winfo_height()
        self.geometry('+500+400')
        self.resizable(False, False)
        self.overrideredirect(1)
        self.bind('<FocusOut>', lambda event: self.destroy())  # <Motion>
        #self.bind('<Button-1>', self.check_this_button)
        # Today
        self.selected = time.strftime("%d.%m.%Y", time.localtime()).split('.')
        self.cal_fr = tk.Frame(self)
        # Calendar create
        self.buildCal(self.selected[1], self.selected[2])

        # ===== EXPEREMENTS =================================

        # fonts for all widgets
        #self.option_add("*Font", self.font)

        # font to use for label widgets
        self.option_add("Label.Font", self.font)

        # make all widgets light blue
        #self.option_add("*Background", "light blue")

        # use gold/black for selections
        #self.option_add("*selectBackground", "gold")
        #self.option_add("*selectForeground", "black")

        #self.textF = tk.Text(self, highlightbackground='#F00')
        #self.textF.grid(columnspan=7, sticky='NSEW')
        #self.textF.insert(tk.INSERT, 'xaxaxa')
        txtt = tk.Label(self, LABEL_OPTIONS)
        txtt.grid(columnspan=7, pady=5)
        txtt.bind('<Button-1>', lambda event: self.doNothing())
        self.vv = tk.StringVar()
        self.vv.set('Не жми на это окошко. Плз :)')
        txtt.config(textvariable=self.vv)

        # ===================================================

    def buildCal(self, month, year):
        cal_array = calendar.TextCalendar(firstweekday=0).itermonthdays4(int(year), int(month))
        nav_frame = tk.Frame(self)
        nav_frame.grid(row=0, columnspan=7, sticky='NSEW')  # raised/sunken ridge/groove flat/solid
        btn_prev = tk.Label(nav_frame, text='<<<', width=5, font=self.font, relief='ridge', highlightthickness=2)
        #btn_prev.grid(row=0, column=0, sticky='NSEW')
        btn_prev.pack(side='left')
        btn_prev.bind('<Button-1>', self.doNothing)

        month_name = tk.Label(nav_frame, text=self.__month_names[int(month)], font=self.font, relief='ridge', highlightthickness=2)
        #month_name.grid(row=0, column=1)
        month_name.pack(side='left', fill=tk.X, expand=True)

        btn_next = tk.Label(nav_frame, text='>>>', font=self.font, borderwidth=2, width=5, relief='ridge', highlightthickness=2)
        #btn_next.grid(row=0, column=2, sticky='NSEW')
        btn_next.bind('<Button-1>', self.doNothing)
        btn_next.pack(side='left')

        for i, week_day in enumerate(self.__week_names):
            weekl = tk.Label(self, text=week_day, font=self.week_font, width=2, pady=0, padx=0, relief='raised', borderwidth=1)
            weekl.grid(row=1, column=i, ipadx=0, ipady=0, sticky='NSEW')

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
        if isinstance(ww['text'], int):
            print(ww.hidden, 'State:', ww['state'])
            ww.config(state="active")
            self.vv.set("Set active value")
            ww.after(1000, lambda: self.vv.set('Не жми на это окошко. Плз :)'))  # after 1000ms

    def change_bg(self, event, bg):     # Like CSS:hover
        event.widget.config(background=bg)

    def doNothing(self, event=None):
        print('Nothing to do')
        for child in self.winfo_children():
            child.destroy()


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
