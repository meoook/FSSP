import calendar
import tkinter as tk
import time
"""
Name: Calendar DatePicker
Version: 1.01
Author: meok
Created: 14.07.2019
Widget parameters:
    date:           (dd.mm.yyyy) to set date
    font_size:             (int) to change widget font size of PopUp window
    not_current_is_nav:   (bool) to navigate with other(not current) month days
    self.__root.date (parameter) from parent class to SET/GET date value
Next version: Trying canvas for year transparent. Del LABEL_OPTIONS :)
    monthlist1 = [1,3,5,7,8,10,12] ## monthlist for months with 31 days.
    monthlist2 = [4,6,9,11] ## monthlist for months with 30 days.
    monthlist3 = 2 ## month with month with 28 days.

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
                 'cursor': 'hand2',                 # Курсор hand1/hand2/circle/clock/cross/dotbox/exchange/fleur/heart/
                                     man/mouse/pirate/plus/shuttle/sizing/spider/spraycan/star/target/tcross/trek/watch/
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
"""


class CalPopup(tk.Label):   # Class polymorph from tk.Label
    # App Settings
    not_current_is_nav = True       # Даты не текущего месяца являются кнопками навигации
    # Locale Settings
    __month_names = ('Zero Month Index', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май',
                     'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь')
    __week_names = ('Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс')

    def __init__(self, master):
        super().__init__(master)
        self.__main = master
        self.__root = self.__main.winfo_toplevel()   # Root window
        # self.__root.wm_attributes('-transparentcolor', self.__root['bg'])     # for transparent root (works bad)
        # String vars to change text values in widget !-> without маргание
        self.__day_vars = [tk.StringVar() for x in range(7*6) if x < 43]
        self.__curr_m_name = tk.StringVar()
        self.__curr_y_name = tk.StringVar()
        # Button for popup
        self.cal_ico = tk.PhotoImage(file='.\\img\\cal_ico.png').subsample(15)
        btn = tk.Button(self.__main, font=self.__main['font'], command=self.__popup,
                       cursor='hand2', highlightbackground='#4B4', bg='#393', fg='#AEA', image=self.cal_ico)
        #btn.config(text='▦')    # ⌨
        btn.pack(side='left', fill='both', padx=3, ipadx=5)
        # Bindings
        self.__bind_hover(btn)
        # Today & Selected
        self.date = time.strftime("%d.%m.%Y", time.localtime())
        self.__main.date = self.date
        # Setting up font size
        self.font_size = 14
        self.__styles_setter()

    @property
    def date(self):
        return '{:02d}.{:02d}.{}'.format(*self.__sel)   # Year no need to be format

    @date.setter
    def date(self, value):
        try:
            time.strptime(value, '%d.%m.%Y')
            self.__sel = [int(n) for n in value.split('.')]
        except ValueError:
            print('\33[91mValue\33[93m', value, '\33[91merror. Must be a date format:\33[93m dd.mm.yyyy\33[0m')
        except TypeError:
            print('\33[91mValue\33[93m', value, '\33[91merror. Must be a string type format:\33[93m dd.mm.yyyy\33[0m')
        else:
            print('\33[94mSelecting date:\33[93m', self.date, '\33[0m')
        # self.__curr = self.__sel[1:3]     # Uncomment & del in PopUp to continue from month we stop, not today month

    @property
    def font_size(self):
        return {'main': self.__font_c, 'weeks': self.__font_w, 'year': self.__font_y, 'nav': self.__font_n}

    @font_size.setter
    def font_size(self, size):
        # Font Settings. Times/Verdana/Lucida/Tempus Sans ITC/Console/Courier/Helvetica
        if isinstance(size, int):
            print('\33[94mChanging font size to:\33[93m', size, '\33[0m')
            size = size if size <= 50 else 50   # Maximum font_size for CSS without errors.
            self.__font_n = ('Console', size)   # Font nav = font cell, mb = font main
            self.__font_y = ('Console', int(size // 2.6))
            self.__font_c = ('Console', size)
            self.__font_w = ('Tempus Sans ITC', int(size // 1.6))
            self.__styles_setter()              # Update styles after changing fonts
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
        self.date = self.__main.date        # Integration with other classes
        self.__curr = self.__sel[1:3]       # Del & uncomment in date.setter to continue from month we stop
        x = self.__main.winfo_rootx()
        y = self.__main.winfo_rooty() + self.__main.winfo_height()
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
        self.__main.focus_force()       # When PopUp lose focus - it's close. See binds.
        self.__main.date = self.date    # Other class integration

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


class DateEntry(tk.Label):      # tk.Frame as defaul but we need to translate Font
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__day = tk.Entry(self, width=2, **kwargs)
        bg, self.hlbg = self.__day['bg'], self.__day['highlightbackground']
        self.__day.config(readonlybackground=bg, bg=self.hlbg)
        dot_dm = tk.Label(self, text='.', **kwargs)
        dot_dm.config(bg=bg)
        self.__month = tk.Entry(self, width=2, readonlybackground=bg, **kwargs)
        self.__month.config(readonlybackground=bg, bg=self.hlbg)
        dot_my = tk.Label(self, text='.', **kwargs)
        dot_my.config(bg=bg)
        self.__year = tk.Entry(self, width=4, readonlybackground=bg, **kwargs)
        self.__year.config(readonlybackground=bg, bg=self.hlbg)

        self.__day.pack(side=tk.LEFT)
        dot_dm.pack(side=tk.LEFT)
        self.__month.pack(side=tk.LEFT)
        dot_my.pack(side=tk.LEFT)
        self.__year.pack(side=tk.LEFT)

        self.__day.bind('<KeyPress>', self._press)
        self.__day.bind('<KeyRelease>', self._release)
        self.__month.bind('<KeyPress>', self._press)
        self.__month.bind('<KeyRelease>', self._release)
        self.__year.bind('<KeyPress>', self._press)
        self.__year.bind('<KeyRelease>', self._release)

    @staticmethod
    def __backspace(part):
        cur = part.index('insert')
        part.delete(cur-1, cur)

    @staticmethod
    def __delete(part):
        cur = part.index('insert')
        part.delete(cur, cur+1)

    @property
    def date(self):
        d, m, y = self.__day.get(), self.__month.get(), self.__year.get()
        d = int(d) if d.isdigit() else 0
        m = int(m) if m.isdigit() else 0
        y = int(y) if y.isdigit() else 0
        return '{:02d}.{:02d}.{}'.format(d, m, y)

    @date.setter
    def date(self, value):
        try:
            d, m, y = value.split('.')
        except Exception as e:
            print('Value not a date format dd.mm.yyyy Change it:', value, e)
        else:
            self.__day.delete(0, tk.END)
            self.__month.delete(0, tk.END)
            self.__year.delete(0, tk.END)

            self.__day.insert(0, d)
            self.__month.insert(0, m)
            self.__year.insert(0, y)

    def __day_part_detect(self, widget):    # Возвращает право и лево от текущей ячейки
        before = False
        nxt = False
        if widget == self.__day:
            nxt = self.__month
        elif widget == self.__month:
            before = self.__day
            nxt = self.__year
        elif widget == self.__year:
            before = self.__month
        return [before, nxt]

    def _press(self, event):
        ww = event.widget                   # Current cell object
        ww.config(state='readonly')         # Make cell readonly (no input allowed but visible cursor
        key = event.keysym                  # Input key (what key was pressed)
        v = ww.get()                        # Value inside the cell
        wth = ww['width']                   # Maximum digits in the cell
        part = self.__day_part_detect(ww)   # Objects: before and next cells or False
        cur_pos = ww.index('insert')        # Cursor position
        selected = ww.selection_present()   # If anything selected in the cell

        if selected and key.isdigit():          # SELECTED
            ww.config(state='normal')
        elif key == 'BackSpace':                # BACKSPACE
            if cur_pos == 0:
                if part[0]:                     # JUMPING TO PREV
                    part[0].focus()
                    self.__backspace(part[0])
            else:                               # CAN BACKSPACE IN CURRENT CELL
                ww.config(state='normal')
        elif key == 'Delete':                   # DELETE
            if cur_pos >= wth or (cur_pos == 0 and len(v) == 0):
                if part[1]:                     # JUMPING TO NEXT
                    part[1].focus()
                    part[1].icursor(0)
                    self.__delete(part[1])
            else:                               # CAN DELETE IN CURRENT CELL
                ww.config(state='normal')
        elif key.isdigit():                     # THE KEY IS DIGIT
            if len(v) >= wth:                   # THE CELL IS FULL
                if cur_pos >= wth:              # CURSOR AT THE END
                    if part[1]:                 # JUMPING TO NEXT
                        part[1].focus()
                        part[1].icursor(0)
                        if len(part[1].get()) >= part[1]['width']:  # NEXT IS FULL
                            self.__delete(part[1])
                            part[1].insert(0, key)      # REPLACE FIRST
                        else:                   # ENOUGH FREE SPACE. INPUT HERE.
                            part[1].insert(0, key)
                    else:                       # NO NEXT CELL TO ADD. REPLACE LAST
                        ww.config(state='normal')
                        self.__backspace(ww)
                else:                           # REPLACE VALUE
                    ww.config(state='normal')
                    self.__delete(ww)
            elif len(v) + 1 >= wth:             # WILL BE FULL AFTER INSERT
                ww.config(state='normal')
                if part[1]:                     # JUMPING TO NEXT
                    part[1].focus()
                    if len(part[1].get()) == part[1]['width']:  # NEXT IS FULL. SELECTING
                        part[1].selection_range(0, 'end')
            else:                               # THERE ARE ENOUGH FREE SELLS. INPUT HERE.
                ww.config(state='normal')
        elif key == 'Left' and cur_pos == 0 and part[0]:                                         # NAVIGATION <<<
            part[0].focus()
        elif key == 'Right' and part[1] and (cur_pos >= wth or (cur_pos == 0 and len(v) == 0)):  # NAVIGATION >>>
            part[1].focus()
        elif key in ('Alt_R', 'Alt_L', 'Control_L', 'Control_R'):   # Need to turn off key combinations
            pass

    def _release(self, event):          # THIS DEF NEEDS REMAKE
        self.__day.config(state='normal')
        self.__month.config(state='normal')
        self.__year.config(state='normal')
        d, m, y = self.__day.get(), self.__month.get(), self.__year.get()
        d = int(d) if d.isdigit() else 0
        m = int(m) if m.isdigit() else 0
        y = int(y) if y.isdigit() else 0
        if 9 < d > 31:
            self.__day.config(bg='#F77')
            self.__day.delete(0, tk.END)
            self.__day.insert(0, '31')
        else:
            self.__day.config(bg=self.hlbg)
        if 9 < m > 12:
            self.__month.config(bg='#F77')
            self.__month.delete(0, tk.END)
            self.__month.insert(0, '12')
        else:
            self.__month.config(bg=self.hlbg)
        if y > 999 and (1900 > y or y > 2100):      # Пока не будет 4 знака (999)
            self.__year.config(bg='#F77')
            #self.__year.delete(0, tk.END)
            #self.__year.insert(0, '20' + str(y)[2:])
        else:
            self.__year.config(bg=self.hlbg)


if __name__ == '__main__':

    # Курсор hand1/hand2/circle/clock/cross/dotbox/exchange/fleur/heart/man/
    # mouse/pirate/plus/shuttle/sizing/spider/spraycan/star/target/tcross/trek/watch/
    root = tk.Tk()
    root.geometry('500x400+500+300')
    tt = DateEntry(root, font=('Times', 40), relief='solid', bd=0)
    tt.pack(side='top')
    app = CalPopup(tt)
    app.font_size = 'aa'
    app.font_size = 24
    app.not_current_is_nav = True
    app.date = '11.0x2.1115'
    app.date = 123
    tt.date = '11.02.2215'
    root.mainloop()


