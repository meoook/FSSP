import calendar
import tkinter as tk
import time

LABEL_OPTIONS = {'activebackground': 'SystemButtonFace',
                 'activeforeground': 'SystemButtonText',
                 'anchor': 'center',        # n/ne/e/se/s/sw/w/nw/center
                 'foreground': 'SystemButtonText',
                 'fg': 'SystemButtonText',  # Same as foreground
                 'background': 'SystemButtonFace',
                 'bg': 'SystemButtonFace',  # Same as background
                 'borderwidth': 1,
                 'bd': 1,                   # Same as borderwidth
                 'image': '',
                 'bitmap': '',
                 'compound': 'none',        # Поведение с картинкой
                 'cursor': 'hand2',         # Курсор hand1/hand2/arrow
                 'disabledforeground': 'SystemDisabledText',
                 'font': 'TkDefaultFont',   # Font (Name, size, bold, italic)
                 'highlightbackground': 'SystemButtonFace',
                 'highlightcolor': 'SystemWindowFrame',
                 'highlightthickness': 2,   # Какой то отступ для эффектов
                 'justify': 'center',
                 'padx': 4,
                 'pady': 2,
                 'relief': 'raised',        # raised/sunken ridge/groove flat/solid - впуклости\выпуклости
                 'state': 'normal',         # active/normal/disabled
                 'takefocus': 0,
                 'text': 'This is a Label',
                 'textvariable': '',        # Link text with this var !-> tk.StringVar()
                 'underline': -1,           # letter position (only 1 letter)
                 'width': 25,
                 'height': 4,
                 'wraplength': 120}         # Text width


class DatePicker(tk.Label):   # Class polimorf from tk.Label (text='01.01.1900' to set date)
    # App Settings
    not_current_is_nav = True       # Даты не текущего месяца являются кнопками навигации
    # Locale Settings
    __month_names = ('Zero Month Index', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май',
                     'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь')
    __week_names = ('Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс')
    # Font Settings
    font_size = 14
    font_main = 'Roboto'
    font_week = 'Console'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root = self.winfo_toplevel()   # Root window
        # Setting up constants
        self.font_size = self.font_size if self.font_size <= 50 else 50  # Maximum font_size for CSS without errors.
        self.__font = (self.font_main, self.font_size)  # , 'bold')  # Times/Verdana/Lucida/Tempus Sans ITC/Console/Courier/Helvetica   italic
        self.__week_font = (self.font_week, int(self.font_size // 1.6))
        # Today & Selected
        if 'text' in kwargs:
            self.sel = [int(n) for n in kwargs.get('text').split('.')]
        else:
            self.sel = [int(n) for n in time.strftime("%d %m %Y", time.localtime()).split()]
        self.__curr = self.sel[1:3]
        # String vars to change text values in widget !-> without маргание
        self.__day_vars = [tk.StringVar() for x in range(7*6) if x < 43]
        self.__curr_m_name = tk.StringVar()
        self.__curr_y_name = tk.StringVar()
        self.__date_value = tk.StringVar()
        # Init label
        self.bind('<Button-1>', lambda event: self.popup())
        self.config(textvariable=self.__date_value)
        self.__set_date()

    def popup(self):
        self.top = tk.Toplevel()        # Don't move or window appear before pressing on picker
        x = self.root.winfo_x() + self.winfo_x() + 9   # Отступ главного окна + отступ внутри окна + погрешность
        y = self.root.winfo_y() + self.winfo_y() + self.winfo_height() + 30     # Тож самое + высота Label + TitleBar
        self.top.geometry('+{}+{}'.format(x, y))    # Смещение окна
        self.top.config(bd=0.4)                     # Граница вокруг календаря
        self.top.resizable(False, False)
        self.top.overrideredirect(1)                # Убрать TitleBar
        self.top.focus_force()                      # Делаем окно активным (для bind: <FocusOut>)
        # Binds
        self.top.bind('<FocusOut>', lambda event: self.top.destroy())   # When the TopLevel lose focus
        self.top.bind('<Button-1>', self.__check_this_button)           # What button we click
        # Building calendar
        self.__nav_build()
        self.__matrix_create_frames()
        self.__matrix_change()

    def __nav_build(self):
        # Navigation
        nav_frame = tk.Frame(self.top)
        nav_frame.pack(side='top', fill=tk.X)  # raised/sunken ridge/groove flat/solid
        btn_prev = tk.Label(nav_frame, text='<<<', font=self.__font, width=4, relief='raised', cursor='hand2', bd=1, highlightbackground='#CCC')
        month_name = tk.Label(nav_frame, textvariable=self.__curr_m_name, font=self.__font, relief='raised', bd=1)
        btn_next = tk.Label(nav_frame, text='>>>', font=self.__font, width=4, relief='raised', cursor='hand2', bd=1, highlightbackground='#CCC')
        year_name = tk.Label(nav_frame, textvariable=self.__curr_y_name, font=('Console', int(self.font_size//2.6)), fg='#111')
        self.__bind_hover(btn_prev)
        self.__bind_hover(btn_next)
        btn_prev.pack(side='left')
        month_name.pack(side='left', fill='x', expand=True, pady=0)
        btn_next.pack(side='left')
        year_name.place(rely=0.0, relx=0.67, relheight=0.4, relwidth=0.09)

    def __matrix_create_frames(self):
        cal_fr = tk.Frame(self.top)
        cal_fr.pack(side='top', fill='both')
        # Week days (here for normal grid)
        for i, week_day in enumerate(self.__week_names):
            week = tk.Label(cal_fr, text=week_day, font=self.__week_font, width=2, relief='raised', bd=1)
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
        for i in range(len(cal_array), 42):
            self.__cells[i].grid_forget()   # Hide other cells

    def __close(self):
        self.__set_date()
        self.root.focus_force()
#        self.top.destroy()

    def __set_date(self):
        self.__date_value.set('.'.join(map(str, self.sel)))

    @property
    def font_s(self):
        print('Getter')
        return self.__font

    @font_s.setter
    def font_s(self, size):
        print('Setter')
        self.__font = (self.font_main, size)

    def __get_style(self, holiday=False, month_sel='current'):
        style = {'font': self.__font, 'width': 2, 'bd': 1, 'cursor': 'hand2', 'fg': '#111',
                 'activebackground': '#090', 'activeforeground': '#AFA', 'highlightthickness': 0,
                 'highlightbackground': '#BBB'}         # this value used for mouse:hover state
        if month_sel == 'current':
            style['background'] = '#999' if holiday else '#CCC'     # Этот месяц: выходной\будень
            style['highlightbackground'] = '#666' if holiday else '#888'
        else:
            style['background'] = '#777' if holiday else '#999'     # Другой месяц: выходной\будень
            style['highlightbackground'] = '#666' if holiday else '#666'
        return style

    # Проверить любое нажание на TopLevel
    def __check_this_button(self, event):
        ww = event.widget
        if 'label' not in str(ww):  # or ww.winfo_name()
            print('GRID Error. Clicked not on {} widget'.format(str(ww)))   # To log
            return False
        try:    # Этот параметр есть только у дней календаря
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
                self.__close()
                return True
        self.__matrix_change()

    @staticmethod
    def __bind_hover(widget):
        enter_color = widget['highlightbackground']
        leave_color = widget['background']
        widget.bind('<Enter>', lambda event, bg=enter_color: widget.config(background=bg))
        widget.bind('<Leave>', lambda event, bg=leave_color: widget.config(background=bg))

    def __curr_change(self, direction):
        if direction == '<<<':
            self.__curr = [12, self.__curr[1]-1] if self.__curr[0] == 1 else [self.__curr[0]-1, self.__curr[1]]
        elif direction == '>>>':
            self.__curr = [1, self.__curr[1]+1] if self.__curr[0] == 12 else [self.__curr[0]+1, self.__curr[1]]


if __name__ == '__main__':
    root = tk.Tk()
    app = DatePicker(root, text='11.7.2019', font=('Times', 24), cursor='hand2', relief='solid', bd=1)
    root.geometry('200x200+500+300')
    app.pack(side='bottom')
    print(app.font_s)
    app.font_s = 34
    print(app.font_s)
    root.mainloop()

