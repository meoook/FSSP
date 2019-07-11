import calendar
import tkinter as tk
from tkinter import ttk
import time
# self.protocol("WM_DELETE_WINDOW", self.close_func)
'''     Examples to use
<Motion>
        # self.update()
        # self.winfo_height()

for child in infoFrame.winfo_children():
    child.destroy()

self.vv = tk.StringVar()
self.vv.set('Не жми на это окошко. Плз :)')
txtt.config(textvariable=self.vv)
ww.after(1000, lambda: self.vv.set('Не жми на это окошко. Плз :)'))  # after 1000ms

'''
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
                 'relief': 'raised',        # raised/sunken ridge/groove flat/solid - впуклости\выпуклости
                 'state': 'normal',
                 'takefocus': 0,
                 'text': 'This is a Label',
                 'textvariable': '',
                 'underline': -1,           # letter position (only 1 letter)
                 'width': 25,
                 'height': 4,
                 'wraplength': 120}         # Text width


class CalPopup(tk.Tk):    # Change to Toplevel
    # Locale Settings
    __month_names = ('Zero Count', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль',
                          'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь')
    __week_names = ('Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс')
    # Font Settings
    font_size = 14
    font = ('Lucida', font_size, 'bold')  # Times/Verdana/Lucida/Tempus Sans ITC/Console/Courier/Helvetica   italic
    week_font = ('Console', int(font_size//1.5))

    def __init__(self):
        super().__init__()
        self.config(borderwidth=1)      # Граница вокруг календаря
        self.geometry('+500+400')       # Смещение окна
        self.resizable(False, False)
        self.overrideredirect(1)        # Убрать TitleBar
        # Binds
        self.bind('<FocusOut>', lambda event: self.destroy())   # When the window lose focus
        self.bind('<Button-1>', self.__check_this_button)       # What button we click
        # Today
        self.selected = time.strftime("%d.%m.%Y", time.localtime()).split('.')
        self.current = self.selected    # mb other way ?
        self.cal_fr = tk.Frame(self)    # What is it ?
        # Calendar create
        self.cal_popup(self.selected[1], self.selected[2])

        # ===== EXPEREMENTS =================================


        # ===================================================

    def cal_popup(self, month, year):
        self.current_m_name = tk.StringVar()
        self.current_m_name.set(self.__month_names[int(month)])
        cal_array = calendar.TextCalendar(firstweekday=0).itermonthdays4(int(year), int(month))

        nav_frame = tk.Frame(self)
        nav_frame.grid(row=0, columnspan=7, sticky='NSEW')  # raised/sunken ridge/groove flat/solid
        btn_prev = tk.Label(nav_frame, text='<<<', font=self.font, width=5, relief='raised', highlightthickness=0, cursor='hand2', borderwidth=1, highlightbackground='#CCC')
        btn_prev.pack(side='left')
        self.__bind_hover(btn_prev)

        month_name = tk.Label(nav_frame, textvariable=self.current_m_name, font=self.font, relief='raised', highlightthickness=0, borderwidth=1)
        month_name.pack(side='left', fill=tk.X, expand=True)

        btn_next = tk.Label(nav_frame, text='>>>', font=self.font, width=5, relief='raised', highlightthickness=0, cursor='hand2', borderwidth=1, highlightbackground='#CCC')
        btn_next.pack(side='left')
        self.__bind_hover(btn_next)

        for i, week_day in enumerate(self.__week_names):
            weekl = tk.Label(self, text=week_day, font=self.week_font, width=2, pady=0, padx=0, relief='raised', borderwidth=1)
            weekl.grid(row=1, column=i, ipadx=0, ipady=0, sticky='NSEW')

        row = 2
        for i, di in enumerate(cal_array):
            day_info = {'day': di[2], 'week': di[3]}
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
                               activebackground='#333', activeforeground='#FFF', disabledforeground='#555',
                               highlightcolor='#DDD', highlightbackground='#BBB', highlightthickness=0)
            current.day_info = day_info      # Vidget parametr
            current.grid(row=row, column=di[3], ipadx=4, ipady=2)

            self.__bind_hover(current)
            row = row + 1 if di[3] == 6 else row

    def __check_this_button(self, event):
        ww = event.widget
        if isinstance(ww['text'], int):
            print(ww.day_info, 'State:', ww['state'])
            if ww.day_info['month'] == 'prev':
                print('Prev month')
            elif ww.day_info['month'] == 'next':
                print('Next month')
            else:
                print('Current month')
                ww.config(state="active")
        elif ww['text'] == '<<<':
            print('Prev month')
        elif ww['text'] == '>>>':
            print('Next month')

    def __bind_hover(self, widget):
        enter_color = widget['highlightbackground']
        leave_color = widget['background']
        widget.bind('<Enter>', lambda event, bg=enter_color: self.__change_bg(event, bg))
        widget.bind('<Leave>', lambda event, bg=leave_color: self.__change_bg(event, bg))

    def __change_bg(self, event, bg):     # Like CSS:hover
        event.widget.config(background=bg)

    def __next_m(self):
        pass

    def __prev_m(self):
        pass

    def __doNothing(self, event=None):
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
