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
                 'anchor': 'center',        # n/ne/e/se/s/sw/w/nw/center
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
                 'state': 'normal',         # active/normal/disabled
                 'takefocus': 0,
                 'text': 'This is a Label',
                 'textvariable': '',
                 'underline': -1,           # letter position (only 1 letter)
                 'width': 25,
                 'height': 4,
                 'wraplength': 120}         # Text width


class CalPopup(tk.Tk):   # Change to Toplevel
    # Locale Settings
    __month_names = ('Zero Month Index', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май',
                     'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь')
    __week_names = ('Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс')
    # Font Settings
    font_size = 34
    font_size = font_size if font_size <= 50 else 50    # Maximum font_size for CSS without errors.
    font = ('Roboto', font_size) #, 'bold')  # Times/Verdana/Lucida/Tempus Sans ITC/Console/Courier/Helvetica   italic
    week_font = ('Console', int(font_size//1.6))
    not_current_is_nav = True       # Даты не текущего месяца являются кнопками навигации

    def __init__(self):
        super().__init__()
        self.config(borderwidth=0.4)    # Граница вокруг календаря
        self.geometry('+500+400')       # Смещение окна но тут надо place(x=0, y=wig.height)
        self.resizable(False, False)
        self.overrideredirect(1)        # Убрать TitleBar
        # Binds
        self.bind('<FocusOut>', lambda event: self.destroy())   # When the window lose focus
        self.bind('<Button-1>', self.__check_this_button)       # What button we click
        # Today & Selected
        self.sel = [int(n) for n in time.strftime("%Y %m %d", time.localtime()).split()]
        self.__curr = self.sel[0:2]
        # String vars to change values without маргание
        self.__day_vars = [tk.StringVar() for x in range(7*6) if x < 43]
        self.__current_m_name = tk.StringVar()
        # Calendar create - 3 строки ниже можно убрать
        self.popup()

    def popup(self):
        # Building calendar
        self.__nav_build()
        self.__matrix_create_frames()
        self.__matrix_change(self.sel[1], self.sel[0])

    def __nav_build(self):
        # Navigation
        nav_frame = tk.Frame(self)
        nav_frame.pack(side='top', fill=tk.X)  # raised/sunken ridge/groove flat/solid
        btn_prev = tk.Label(nav_frame, text='<<<', font=self.font, width=4, relief='raised', highlightthickness=0, cursor='hand2', borderwidth=1, highlightbackground='#CCC')
        month_name = tk.Label(nav_frame, textvariable=self.__current_m_name, font=self.font, relief='raised', highlightthickness=0, borderwidth=1)
        btn_next = tk.Label(nav_frame, text='>>>', font=self.font, width=4, relief='raised', highlightthickness=0, cursor='hand2', borderwidth=1, highlightbackground='#CCC')
        self.__bind_hover(btn_prev)
        self.__bind_hover(btn_next)
        btn_prev.pack(side='left')
        month_name.pack(side='left', fill=tk.X, expand=True, pady=0.5)
        btn_next.pack(side='left')

    def __matrix_create_frames(self):
        cal_fr = tk.Frame(self)
        cal_fr.pack(side='top', fill='both')
        # Week days (here for normal grid)
        for i, week_day in enumerate(self.__week_names):
            week = tk.Label(cal_fr, text=week_day, font=self.week_font, width=2, relief='raised', borderwidth=1)
            week.grid(row=0, column=i, ipadx=0, ipady=0, sticky='NSEW')
        self.__cells = [tk.Label(cal_fr, textvariable=self.__day_vars[i], relief='ridge') for i in range(42)]

    def __matrix_grid(self):
        row = 0
        for i in range(42):
            row = row + 1 if i % 7 == 0 else row
            x = i-(row-1)*7
            if i in range(self.__curr[2]):
                self.__cells[i].grid(row=row, column=x, ipadx=4, ipady=0)
            else:
                #self.cells[i].grid_remove()
                self.__cells[i].grid_forget()

    def __matrix_change(self, month, year):
        #self.__curr.append(len(list(cal_array)))
        self.__current_m_name.set(self.__month_names[month])
        cal_array = calendar.TextCalendar(firstweekday=0).itermonthdays4(year, month)
        # COUNT DAYS AND FINISH GRID !!!
        # COUNT DAYS AND FINISH GRID !!!
        # COUNT DAYS AND FINISH GRID !!!
        # COUNT DAYS AND FINISH GRID !!!
        # COUNT DAYS AND FINISH GRID !!!
        xx = len([*cal_array])
        self.__curr.append(xx)
        print(xx)
        for i, day in enumerate(cal_array):
            self.__day_vars[i].set(day[2])
            holiday = True if day[3] in (5, 6) else False
            # Проверка на дни с прошлого\текущего\следующего месяца
            what_month = 'current'
            if i < 7 and day[2] > 20:
                what_month = 'prev'
            elif i > 20 and day[2] < 7:
                what_month = 'next'
            # Set Label style
            state = 'active' if all([self.sel[0] == day[0], self.sel[1] == day[1], self.sel[2] == day[2]]) else 'normal'
            self.__cells[i].config(self.__get_style(holiday, what_month), state=state)
            self.__cells[i].what_m = what_month     # Не нравится ему так, хотя в другом файле для dict норм
            self.__bind_hover(self.__cells[i])
        self.__matrix_grid()

    def __cal_destroy(self):
        print('Remove all child')
        for child in self.__cal_fr.winfo_children():
            # child.destroy()
            child.grid_remove()

    def __get_style(self, holiday=False, month_sel='current'):
        style = {'font': self.font, 'width': 2, 'borderwidth': 1, 'cursor': 'hand2', 'foreground': '#111',
                 'activebackground': '#090', 'activeforeground': '#AFA', 'highlightthickness': 0,
                 'highlightbackground': '#BBB'}         # this value used for mouse:hover state
        if month_sel == 'current':
            style['background'] = '#999' if holiday else '#CCC'     # этот\выходной
            style['highlightbackground'] = '#666' if holiday else '#888'
        else:
            style['background'] = '#777' if holiday else '#999'     # Другой\выходной
            style['highlightbackground'] = '#666' if holiday else '#666'
        return style

    def __check_this_button(self, event):
        ww = event.widget
        var = ww.what_m
        print(var)
        if 'label' not in str(ww):  # or ww.winfo_name()
            print('GRID Error. Clicked not on {} widget'.format(str(ww)))
            return False
        if isinstance(ww['text'], int):
            if var == 'prev':
                self.__prev_m()
            elif var == 'next':
                self.__next_m()
            else:
                self.__day_select(ww)
        elif ww['text'] == '<<<':
            self.__change_month('prev')
        elif ww['text'] == '>>>':
            self.__change_month('next')
        else:
            print('You press Nav bar')

    # bind: mouse on widget
    def __bind_hover(self, widget):
        enter_color = widget['highlightbackground']
        leave_color = widget['background']
        widget.bind('<Enter>', lambda event, bg=enter_color: widget.config(background=bg))
        widget.bind('<Leave>', lambda event, bg=leave_color: widget.config(background=bg))

    def __prev_m(self):
        print('Prev month')

    def __next_m(self):
        print('Next month')

    def __change_month(self, direction):
        if direction == 'next':
            self.__curr = [self.__curr[0]+1, 1] if self.__curr[1] == 12 else [self.__curr[0], self.__curr[1]+1]
        elif direction == 'prev':
            self.__curr = [self.__curr[0]-1, 12] if self.__curr[1] == 1 else [self.__curr[0], self.__curr[1]-1]
        self.__cal_build(self.__curr[1], self.__curr[0])
        print('result', self.__curr)

    def __day_select(self, widget):
        widget.config(state="active")

    def __save_n_close(self):
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
