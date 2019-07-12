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


class CalPopup(tk.Tk):    # Change to Toplevel
    # Locale Settings
    __month_names = ('Zero Month Index', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май',
                     'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь')
    __week_names = ('Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс')
    # Font Settings
    font_size = 34
    font = ('Lucida', font_size, 'bold')  # Times/Verdana/Lucida/Tempus Sans ITC/Console/Courier/Helvetica   italic
    week_font = ('Console', int(font_size//1.5))

    def __init__(self):
        super().__init__()
        self.config(borderwidth=0.4)      # Граница вокруг календаря
        self.geometry('+500+400')       # Смещение окна но тут надо place(x=0, y=wig.height)
        self.resizable(False, False)
        self.overrideredirect(1)        # Убрать TitleBar
        # Binds
        self.bind('<FocusOut>', lambda event: self.destroy())   # When the window lose focus
        self.bind('<Button-1>', self.__check_this_button)       # What button we click
        # Today & Selected
        self.sel = ([int(n) for n in time.strftime("%Y %m %d", time.localtime()).split()])
        # WARNING LIST PROBLEM. Cant assign self.__curr[1]
        # WARNING LIST PROBLEM. Cant assign self.__curr[1]
        # WARNING LIST PROBLEM. Cant assign self.__curr[1]
        self.__curr = self.sel[:2]
        print(type(self.__curr), type(self.sel))
        self.__curr = list(self.__curr)
        print(type(self.__curr), type(self.sel))
        self.__current_m_name = tk.StringVar()
        # Calendar create
        self.__cal_fr = tk.Frame(self)
        self.cal_popup(self.sel[1], self.sel[0])

    # Popup
    def cal_popup(self, month, year):
        self.__current_m_name.set(self.__month_names[month])
        # Navigation
        nav_frame = tk.Frame(self)
        nav_frame.pack(side='top', fill=tk.X)  # raised/sunken ridge/groove flat/solid
        btn_prev = tk.Label(nav_frame, text='<<<', font=self.font, width=5, relief='raised', highlightthickness=0, cursor='hand2', borderwidth=1, highlightbackground='#CCC')
        month_name = tk.Label(nav_frame, textvariable=self.__current_m_name, font=self.font, relief='raised', highlightthickness=0, borderwidth=1)
        btn_next = tk.Label(nav_frame, text='>>>', font=self.font, width=5, relief='raised', highlightthickness=0, cursor='hand2', borderwidth=1, highlightbackground='#CCC')
        self.__bind_hover(btn_prev)
        self.__bind_hover(btn_next)
        btn_prev.pack(side='left')
        month_name.pack(side='left', fill=tk.X, expand=True, pady=0.5)
        btn_next.pack(side='left')

        self.__cal_fr.pack(side='top')
        # Week days
        for i, week_day in enumerate(self.__week_names):
            weekl = tk.Label(self.__cal_fr, text=week_day, font=self.week_font, width=2, pady=0, padx=0, relief='raised', borderwidth=1)
            weekl.grid(row=0, column=i, ipadx=0, ipady=0, sticky='NSEW')

        self.__cal_build(month, year)

    def __cal_build(self, month, year):
        self.__cal_destroy()
        cal_array = calendar.TextCalendar(firstweekday=0).itermonthdays4(year, month)
        row = 1
        for i, day in enumerate(cal_array):
            day_info = {'year': day[0], 'month': day[1], 'day': day[2], 'week': day[3],
                        'holiday': True if day[3] in (5, 6) else False, 'month_sel': 'current'}
            # Проверка на дни с прошлого\текущего\предыдущего месяца
            if i < 7 and day[2] > 20:
                day_info['month_sel'] = 'prev'
            elif i > 20 and day[2] < 7:
                day_info['month_sel'] = 'next'
            # Set Label style
            cell_style = self.__get_style(day_info['holiday'], day_info['month_sel'])
            state = 'active' if all([self.sel[0] == day[0], self.sel[1] == day[1], self.sel[2] == day[2]]) else 'normal'
            current = tk.Label(self.__cal_fr, cell_style, text=day[2], state=state, relief='ridge')
            current.grid(row=row, column=day[3], ipadx=4, ipady=2)
            current.day_info = day_info
            self.__bind_hover(current)
            row = row + 1 if day[3] == 6 else row

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

    def __cal_destroy(self):
        print('Nothing to do')
        for child in self.__cal_fr.winfo_children():
            child.destroy()

    def __check_this_button(self, event):
        ww = event.widget
        if 'label' not in str(ww):
            print('GRID Error. Clicked not on {} widget'.format(str(ww)))
            return False
        if isinstance(ww['text'], int):
            print(ww.day_info, 'State:', ww['state'])
            if ww.day_info['month_sel'] == 'prev':
                self.__prev_m()
            elif ww.day_info['month_sel'] == 'next':
                self.__next_m()
            else:
                self.__date_selected(ww)
        elif ww['text'] == '<<<':
            self.change_month('prev')
        elif ww['text'] == '>>>':
            self.change_month('next')
        else:
            print('You press Nav bar')

    # bind: mouse on widget
    def __bind_hover(self, widget):
        enter_color = widget['highlightbackground']
        leave_color = widget['background']
        widget.bind('<Enter>', lambda event, bg=enter_color: self.__change_bg(event, bg))
        widget.bind('<Leave>', lambda event, bg=leave_color: self.__change_bg(event, bg))

    def __change_bg(self, event, bg):
        event.widget.config(background=bg)

    def __prev_m(self):
        print('Prev month')

    def __next_m(self):
        print('Next month')

    def change_month(self, direction):
        if direction == 'next' and self.__curr[1] == 12:
            self.__curr[0] = self.__curr[0] + 1
        else:
            print('next', self.__curr[1])
            self.__curr[1] += 1
            print(self.__curr[1])
        if direction == 'prev' and self.__curr == 0:
            self.__curr = [self.__curr[0] - 1, 12]
        else:
            self.__curr[1] -= 1
        print(self.__curr)

    def __date_selected(self, widget):
        print('Current month')
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
