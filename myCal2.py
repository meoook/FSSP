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
    font_size = 24
    font_size = font_size if font_size <= 50 else 50    # Maximum font_size for CSS without errors.
    font = ('Roboto', font_size) #, 'bold')  # Times/Verdana/Lucida/Tempus Sans ITC/Console/Courier/Helvetica   italic
    week_font = ('Console', int(font_size//1.6))
    not_current_is_nav = False       # Даты не текущего месяца являются кнопками навигации

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
        self.sel = [int(n) for n in time.strftime("%d %m %Y", time.localtime()).split()]
        self.__curr = self.sel[1:3]
        # String vars to change values without маргание
        self.__day_vars = [tk.StringVar() for x in range(7*6) if x < 43]
        self.__curr_m_name = tk.StringVar()
        self.__curr_y_name = tk.StringVar()
        # Calendar create - 3 строки ниже можно убрать
        self.popup()

    def popup(self):
        # Building calendar
        self.__nav_build()
        self.__matrix_create_frames()
        self.__matrix_change()

    def __nav_build(self):
        # Navigation
        nav_frame = tk.Frame(self)
        nav_frame.pack(side='top', fill=tk.X)  # raised/sunken ridge/groove flat/solid
        btn_prev = tk.Label(nav_frame, text='<<<', font=self.font, width=4, relief='raised', highlightthickness=0, cursor='hand2', borderwidth=1, highlightbackground='#CCC')
        month_name = tk.Label(nav_frame, textvariable=self.__curr_m_name, font=self.font, relief='raised', highlightthickness=0, borderwidth=1)
        btn_next = tk.Label(nav_frame, text='>>>', font=self.font, width=4, relief='raised', highlightthickness=0, cursor='hand2', borderwidth=1, highlightbackground='#CCC')
        year_name = tk.Label(nav_frame, textvariable=self.__curr_y_name, font=('Console', int(self.font_size//2.6)), fg='#111')
        self.__bind_hover(btn_prev)
        self.__bind_hover(btn_next)
        btn_prev.pack(side='left')
        month_name.pack(side='left', fill='x', expand=True, pady=0.5)
        btn_next.pack(side='left')
        year_name.place(rely=0.0, relx=0.67, relheight=0.4, relwidth=0.09)

    def __matrix_create_frames(self):
        cal_fr = tk.Frame(self)
        cal_fr.pack(side='top', fill='both')
        # Week days (here for normal grid)
        for i, week_day in enumerate(self.__week_names):
            week = tk.Label(cal_fr, text=week_day, font=self.week_font, width=2, relief='raised', borderwidth=1)
            week.grid(row=0, column=i, ipadx=0, ipady=0, sticky='NSEW')
        self.__cells = [tk.Label(cal_fr, textvariable=self.__day_vars[i], relief='ridge') for i in range(42)]

    def __matrix_change(self):
        self.__curr_m_name.set(self.__month_names[self.__curr[0]])
        self.__curr_y_name.set(self.__curr[1])
        cal_array = list(calendar.TextCalendar(firstweekday=0).itermonthdays4(self.__curr[1], self.__curr[0]))
        row = 0
        for i, day in enumerate(cal_array):
            self.__day_vars[i].set(day[2])
            holiday = True if day[3] in (5, 6) else False
            # Direction: дни с прошлого\текущего\следующего месяца
            what_month = 'current'
            if i < 7 and day[2] > 20:
                what_month = '<<<'
            elif i > 20 and day[2] < 7:
                what_month = '>>>'
            # Set Label style
            state = 'active' if all([self.sel[0] == day[2], self.sel[1] == day[1], self.sel[2] == day[0]]) else 'normal'
            cell, style = self.__cells[i], self.__get_style(holiday, what_month)
            cell.config(style, state=state)
            row = row + 1 if day[3] == 0 else row
            cell.grid(row=row, column=day[3], ipadx=4, ipady=0)
            cell.what_m = what_month
            self.__bind_hover(cell)
        self.__matrix_grid(len(cal_array))

    def __matrix_grid(self, n):
        for i in range(n, 42):
            #self.cells[i].grid_remove()
            self.__cells[i].grid_forget()

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
        if 'label' not in str(ww):  # or ww.winfo_name()
            print('GRID Error. Clicked not on {} widget'.format(str(ww)))   # To log
            return False
        try:
            ww.what_m
        except Exception as e:
            if ww['text'] in ('<<<', '>>>'):
                self.__curr_change(ww['text'])
            else:
                print('You press', ww, e)       # To log
                return False
        if isinstance(ww['text'], int) and ww['text'] < 32:
            self.__curr_change(ww.what_m)
            if not self.not_current_is_nav or ww.what_m == 'current':
                self.sel = [ww['text'], self.__curr[0], self.__curr[1]]
                self.__save_n_close()
                #return True
        print(self.__curr, self.sel)
        self.__matrix_change()

    # bind: mouse on widget
    def __bind_hover(self, widget):
        enter_color = widget['highlightbackground']
        leave_color = widget['background']
        widget.bind('<Enter>', lambda event, bg=enter_color: widget.config(background=bg))
        widget.bind('<Leave>', lambda event, bg=leave_color: widget.config(background=bg))

    def __curr_change(self, direction):
        if direction == '<<<':
            self.__curr = [12, self.__curr[1]-1] if self.__curr[0] == 1 else [self.__curr[0]-1, self.__curr[1]]
        elif direction == '>>>':
            self.__curr = [1, self.__curr[1]+1] if self.__curr[0] == 12 else [self.__curr[0]+1, self.__curr[1]]

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
