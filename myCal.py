import calendar
import tkinter as tk
import time
"""
Name: Calendar DatePicker
Version: 1.01
Author: meok
Created: 14.07.2019
Widget parameters:
    date:         (dd.mm.yyyy) to set date
    font_size:           (int) to change widget font size of PopUp window
    not_current_is_nav: (bool) to navigate with other(not current) month days
Next version: Trying canvas for year transparent. Del LABEL_OPTIONS :)
"""
LABEL_OPTIONS = {'activebackground': 'SystemButtonFace',    # BG color when state = disabled
                 'activeforeground': 'SystemButtonText',    # Font color when state = disabled
                 'anchor': 'center',                # n/ne/e/se/s/sw/w/nw/center
                 'justify': 'center',               # Same as anchor ?
                 'foreground': 'SystemButtonText',  # Text color
                 'fg': 'SystemButtonText',          # Same as foreground
                 'background': 'SystemButtonFace',  # BG color
                 'bg': 'SystemButtonFace',          # Same as background
                 'borderwidth': 1,                  # Border width (in pixels)
                 'bd': 1,                           # Same as borderwidth
                 'font': 'TkDefaultFont',           # Font (Name, size, bold, italic)
                 'cursor': 'hand2',                 # Курсор hand1/hand2/arrow/...
                 'relief': 'raised',                # raised/sunken ridge/groove flat/solid
                 'textvariable': '',                # Link text with this var !-> tk.StringVar()
                 'text': 'This is a Label',         # Text for the label (if textvariable not set)
                 'image': '',                       # The image must be set: tk.PhotoImage(file='.\img\test.gif')
                 'bitmap': '',
                 'compound': 'none',                # Поведение с картинкой
                 'disabledforeground': 'SystemDisabledText',    # Text color when state = disabled
                 'highlightbackground': 'SystemButtonFace',     # Effects bg
                 'highlightcolor': 'SystemWindowFrame',         # Effects color
                 'highlightthickness': 2,           # Какой то отступ для эффектов (in pixels)
                 'state': 'normal',                 # active/normal/disabled
                 'underline': -1,                   # letter position (only 1 letter)
                 'padx': 4,                         # In pixels
                 'pady': 2,                         # In pixels
                 'width': 25,                       # In chars
                 'height': 4,                       # In chars
                 'wraplength': 12,                  # Text maximum width in cell (in chars)
                 'takefocus': 0}


class DatePicker(tk.Label):   # Class polymorph from tk.Label
    # App Settings
    not_current_is_nav = True       # Даты не текущего месяца являются кнопками навигации
    # Locale Settings
    __month_names = ('Zero Month Index', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май',
                     'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь')
    __week_names = ('Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__root = self.winfo_toplevel()   # Root window
        # self.__root.wm_attributes('-transparentcolor', self.__root['bg'])     # for transparent root (works bad)
        # String vars to change text values in widget !-> without маргание
        self.__day_vars = [tk.StringVar() for x in range(7*6) if x < 43]
        self.__curr_m_name = tk.StringVar()
        self.__curr_y_name = tk.StringVar()
        self.__date_value = tk.StringVar()
        # Init label
        self.bind('<Button-1>', lambda event: self.__popup())
        self.config(textvariable=self.__date_value)
        # Today & Selected
        self.date = time.strftime("%d.%m.%Y", time.localtime())
        # Setting up font size
        self.font_size = 14
        self.__styles_setter()

    @property
    def date(self):
        return '{:02d}.{:02d}.{}'.format(*self.__sel)

    @date.setter
    def date(self, value):
        # Today & Selected
        try:
            time.strptime(value, '%d.%m.%Y')
            self.__sel = [int(n) for n in value.split('.')]
        except ValueError:
            print('\33[91mValue\33[93m', value, '\33[91merror. Must be a date format:\33[93m dd.mm.yyyy\33[0m')
        except TypeError:
            print('\33[91mValue\33[93m', value, '\33[91merror. Must be a string type format:\33[93m dd.mm.yyyy\33[0m')
        else:
            print('\33[94mChanging date to:\33[93m', self.date, '\33[0m')
            self.__date_value.set(self.date)
        # self.__curr = self.__sel[1:3]     # Uncomment & del in PopUp to continue from month we stop, not today month

    @property
    def font_size(self):
        return {'main': self.__font_c, 'weeks': self.__font_w, 'year': self.__font_y, 'nav': self.__font_n}

    @font_size.setter
    def font_size(self, size):
        # Font Settings. Times/Verdana/Lucida/Tempus Sans ITC/Console/Courier/Helvetica
        if isinstance(size, int):
            print('\33[94mChanging font size to:\33[93m', size, '\33[0m')
            size = size if size <= 50 else 50  # Maximum font_size for CSS without errors.
            self.__font_n = ('Console', size)   # Font nav = font cell, mb = font main
            self.__font_y = ('Console', int(size // 2.6))
            self.__font_c = ('Console', size)
            self.__font_w = ('Tempus Sans ITC', int(size // 1.6))
            self.__styles_setter()            # Update styles after changing fonts
        else:
            print('\33[91mSize must be int value. Using defaults.\33[0m')
        print('\33[94mUsing fonts:\33[0m')
        print('\33[93m{:5s} \33[92m{main}\33[93m\n{:5s} \33[92m{weeks}\33[93m\n{:5s} \33[92m{year}\33[93m\n{:5s} '
              '\33[92m{nav}\33[0m'.format(*self.font_size, **self.font_size), '\33[0m')

    def __styles_setter(self):
        default = {'fg': '#111', 'bg': '#EEE', 'bd': 1, 'relief': 'raised',
                       'activebackground': '#090', 'activeforeground': '#AFA',
                       'highlightthickness': 0, 'highlightbackground': '#CCC'}  # this value used for mouse:hover state
        self.__style_nav = {'font': self.__font_n, **default, 'pady': 5}
        self.__style_year = {'font': self.__font_y, **default, 'relief': 'flat', 'fg': '#222'}
        self.__style_week = {'font': self.__font_w, **default, 'width': 2}
        self.__style_cell = {'font': self.__font_c, **default, 'width': 2, 'cursor': 'hand2'}
        # More cell styles in get_cell_style function.

    def __popup(self):
        top = tk.Toplevel()
        self.__curr = self.__sel[1:3]       # Del & uncomment in date.setter to continue from month we stop
        x = self.__root.winfo_x() + self.winfo_x() + 9       # Отступ главного окна + отступ внутри окна + погрешность
        y = self.__root.winfo_y() + self.winfo_y() + self.winfo_height() + 30  # Тож самое + высота Label + TitleBar(30)
        top.geometry('+{}+{}'.format(x, y))    # Смещение окна
        top.config(bd=0.4)                     # Граница вокруг календаря
        top.resizable(False, False)
        top.overrideredirect(1)                # Убрать TitleBar
        top.focus_force()                      # Делаем окно активным (для bind: <FocusOut>)
        # Binds
        top.bind('<FocusOut>', lambda event: top.destroy())   # When PopUp lose focus
        top.bind('<Button-1>', self.__check_this_button)      # What button we click
        # Building calendar
        self.__nav_build(top)
        self.__matrix_create_frames(top)
        self.__matrix_change()

    def __nav_build(self, top):
        nav_frame = tk.Frame(top)
        nav_frame.pack(side='top', fill=tk.X)  # raised/sunken ridge/groove flat/solid
        btn_prev = tk.Label(nav_frame, self.__style_nav, text='<<<', width=4, cursor='hand2')
        month_name = tk.Label(nav_frame, self.__style_nav, textvariable=self.__curr_m_name)
        btn_next = tk.Label(nav_frame, self.__style_nav, text='>>>', width=4, cursor='hand2')
        year_name = tk.Label(nav_frame, self.__style_year, textvariable=self.__curr_y_name)
        self.__bind_hover(btn_prev)
        self.__bind_hover(btn_next)
        btn_prev.pack(side='left')
        month_name.pack(side='left', fill='x', expand=True, pady=0)
        btn_next.pack(side='left')
        year_name.place(rely=0.01, relx=0.667, relheight=0.4, relwidth=0.09)

    def __matrix_create_frames(self, top):
        cal_fr = tk.Frame(top)
        cal_fr.pack(side='top', fill='both')
        # Week days (here for normal grid) ! Need styling for this
        for i, week_day in enumerate(self.__week_names):
            week = tk.Label(cal_fr, self.__style_week, text=week_day)
            week.grid(row=0, column=i, ipadx=0, ipady=0, sticky='NSEW')
        self.__cells = [tk.Label(cal_fr, self.__style_cell, textvariable=self.__day_vars[i]) for i in range(42)]

    # Insert values in matrix
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
            state = 'active' if self.__sel == [day[2], day[1], day[0]] else 'normal'
            cell, style = self.__cells[i], self.__get_cell_style(holiday, what_month)
            cell.config(style, state=state)
            row = row + 1 if day[3] == 0 else row
            cell.grid(row=row, column=day[3], ipadx=4, ipady=0)
            cell.what_m = what_month
            self.__bind_hover(cell)
        for i in range(len(cal_array), 42):
            self.__cells[i].grid_forget()   # Hide other cells

    # Check click on PopUp !-> curr_change or date_selected
    def __check_this_button(self, event):
        ww = event.widget
        if 'label' not in str(ww):  # or ww.winfo_name()
            print('\33[91mGRID Error. Clicked not on {} widget\33[0m'.format(ww))   # To log
            return False
        try:    # Этот параметр есть только у дней календаря
            ww.what_m
        except Exception as e:
            if ww['text'] in ('<<<', '>>>'):
                self.__curr_change(ww['text'])
            else:
                print('\33[94mYou press', ww, e, '\33[0m')       # To log
                return False
        if isinstance(ww['text'], int) and ww['text'] < 32:
            self.__curr_change(ww.what_m)
            if not self.not_current_is_nav or ww.what_m == 'current':
                self.__sel = [ww['text'], self.__curr[0], self.__curr[1]]
                self.__date_selected()
                return True
        self.__matrix_change()

    # Change current month, year
    def __curr_change(self, direction):
        if direction == '<<<':
            self.__curr = [12, self.__curr[1]-1] if self.__curr[0] == 1 else [self.__curr[0]-1, self.__curr[1]]
        elif direction == '>>>':
            self.__curr = [1, self.__curr[1]+1] if self.__curr[0] == 12 else [self.__curr[0]+1, self.__curr[1]]

    # Save and close
    def __date_selected(self):
        self.date = '.'.join(map(str, self.__sel))
        self.__root.focus_force()     # When PopUp lose focus - it's close. See binds.

    @staticmethod
    def __bind_hover(widget):
        enter_color = widget['highlightbackground']
        leave_color = widget['background']
        widget.bind('<Enter>', lambda event, bg=enter_color: widget.config(background=bg))
        widget.bind('<Leave>', lambda event, bg=leave_color: widget.config(background=bg))

    @staticmethod
    def __get_cell_style(holiday=False, month_sel='current'):
        style = {'fg': '#111'}
        if month_sel == 'current':
            style['background'] = '#999' if holiday else '#CCC'     # Этот месяц: выходной\будень
            style['highlightbackground'] = '#666' if holiday else '#888'
        else:
            style['background'] = '#595959' if holiday else '#757575'     # Другой месяц: выходной\будень
            style['highlightbackground'] = '#555' if holiday else '#555'
            style['fg'] = '#DDD'
        return style


if __name__ == '__main__':
    root = tk.Tk()
    app = DatePicker(root, font=('Times', 34), cursor='hand2', relief='solid', bd=1)
    root.geometry('500x500+500+300')
    app.pack(side='top')
    app.font_size = 'aa'
    app.font_size = 34
    app.not_current_is_nav = True
    app.date = '11.0x2.1115'
    app.date = 123
    app.date = '11.02.1115'
    root.mainloop()


