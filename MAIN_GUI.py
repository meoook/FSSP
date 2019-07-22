import configparser
import requests
import time
import re
import psycopg2
import os
import tkinter as tk
from tkinter import ttk
from myCal import DateEntry, CalPopup
from fssp import FSSP

'''
COLORS
INFO    93
ERROR   33
CRIT    31
OK      94
FAIL    91
'''

# Класс Базы Данных
class DataBase:
    def __init__(self, db_connect=None):
        self.conn = None
        self.cur = None

        if db_connect:
            self.open(db_connect)

    # Открываем соединение с БД
    def open(self, pa):
        self.conn = psycopg2.connect(host=pa['host'], database=pa['dbname'], user=pa['user'], password=pa['pwd'])
        self.cur = self.conn.cursor()

    # Делаем SELECT
    def select_sql(self, date=None, znak=None):
        select = "SELECT upper(lastname), upper(firstname), upper(secondname), to_char(birthday, 'DD.MM.YYYY'), " \
                 "to_char(creation_date, 'DD.MM.YYYY hh24:mi:ss'), court_adr, court_numb, reestr, " \
                 "md5(concat(upper(lastname), upper(firstname), upper(secondname), to_char(birthday, 'DD.MM.YYYY'))) " \
                 "FROM fssp as v WHERE creation_date::date "
        select += ">=" if znak else "="
        select += "'" + date + "'" if date else "current_date"  # Нужна проверочка - что date соответсвует формату
        select += " ORDER BY creation_date DESC"
        self.cur.execute(select)
        result = self.cur.fetchall()
        return result

    # Закрываем соединение с БД - не понятно, работает ли :)
    def close(self):
        print('SQL close')
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Основной класс программы
class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # Отобразить встроенные стили
        style = ttk.Style()
        print(style.theme_names())
        style.theme_use('vista')

        # App window Settings
        self.title("Проверяльщик ФССП")                    # Название
        self.geometry('+500+300')    # Смещение окна
        self.resizable(False, False)                       # Растягивается
        self.iconbitmap(self, default='.\\img\\ico.ico')   # Иконка приложения
        # Load Config
        self.get_config()
        self.save_cfg()
        # Отображаемые модули\виджиты на главном фрейме
        self.menu_bar()
        self.tool_bar()
        self.log_window()
        # Создаем верхний фрейм, куда будем пихать другие страницы\фреймы
        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True, padx=2, pady=1)
        # Загружаем фреймы
        self.frames = {}
        for F in (MainPage, SettingsPage):    # Список всех фреймов
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')
        # Подключаемся к ДБ
        self.db = DataBase({'host': self.cfg['POSTGRES']['HOST'], 'dbname': self.cfg['POSTGRES']['DBNAME'],
                            'user': self.cfg['POSTGRES']['USER'], 'pwd': self.cfg['POSTGRES']['PWD']})
        # Вызов класса ФССП
        self.fssp = FSSP(self.cfg['FSSP.RU']['TOKEN'], self.cfg['FSSP.RU']['PAUSE'], self.cfg['FSSP.RU']['URL'])
        # При запуске показываем заглавную страницу
        self.show_frame(MainPage)

    # Главное меню (полоска)
    def menu_bar(self):
        menubar = tk.Menu(self)
        # File SubMenu
        file = tk.Menu(menubar, tearoff=0)
        file.add_command(label='New', command=lambda: self.show_frame(MainPage))
        file.add_command(label='Open')
        file.add_command(label='Save')
        file.add_command(label='Close')
        file.add_command(label='Options', command=lambda: self.show_frame(SettingsPage))
        file.add_separator()
        file.add_command(label='Exit', command=self.quit)
        # Edit SubMenu
        edit = tk.Menu(menubar, tearoff=0)
        edit.add_command(label="Undo")
        edit.add_separator()
        edit.add_command(label="Cut")
        edit.add_command(label="Copy")
        edit.add_command(label="Paste")
        edit.add_command(label="Delete")
        edit.add_command(label="Select All")
        # Info SubMenu
        info = tk.Menu(menubar, tearoff=0)
        info.add_command(label="About")
        # Menu elements
        menubar.add_cascade(label='File', menu=file)
        menubar.add_cascade(label="Edit", menu=edit)
        menubar.add_cascade(label="Help", menu=info)
        # Включаем для Object
        self.config(menu=menubar)

    # Меню из иконок
    def tool_bar(self):
        # Отдельный фрейм для ToolBar
        toolbar = tk.Frame(self)
        toolbar.pack(side='top', fill=tk.X, padx=2)
        self.bind('<ButtonRelease>', lambda e: self.change_number_name())     # Or check gui funct

        font = ('helvetica', 27)     # "Arial 24"
        self.settings_ico = tk.PhotoImage(file='.\\img\\setting4.png').subsample(6)
        self.sql_ico = tk.PhotoImage(file='.\\img\\sql2.png').subsample(15)
        self.fssp_ico = tk.PhotoImage(file='.\\img\\fssp.png').subsample(8)
        btn1 = tk.Button(toolbar, command=lambda: self.show_frame(SettingsPage), image=self.settings_ico, bg='#393')
        btn1.pack(side='left', fill='both')

        select_label = tk.Label(toolbar, font=font, text='Найти нарушителей', bg='#beb', fg='#393')
        select_label.pack(side='left', fill='both')

        # STYLE STYLE STYLE :)
        st = ttk.Style()
        st.configure("Line.TSeparator", background="#fff")
        st.configure("C.TButton", padding=(0, 0, 0, 0))
        st.map("C.TButton",
               foreground=[('pressed', 'red'), ('active', 'green')],
               background=[('pressed', '!disabled', 'black'), ('active', 'white')],
               relief=[('pressed', '!disabled', 'sunken')])
        # END STYLE
        self.select_znak = TkCombo(toolbar, 'За', 'С',  font=font, width=3, bg='#beb', fg='#393')

        self.select_date = DateEntry(toolbar, font=font,  bd=0, bg='#beb', fg='#393')
        self.select_date.config(relief='groove', bd=2)
        self.select_date.pack(side='left', fill='both')
        CalPopup(self.select_date)
        self.select_date.date = '24.05.2019'

        self.__number_name = tk.StringVar()
        number_name = tk.Label(toolbar, font=font, textvariable=self.__number_name, bg='#beb', fg='#393')
        number_name.pack(side='left', fill='both')
        self.change_number_name()

        btn2 = tk.Button(toolbar, command=self.get_req_data, image=self.sql_ico, bg='#393')
        btn2.pack(side='left', fill='both', ipadx=4)

        btn3 = tk.Button(toolbar, command=lambda: self.get_fssp_data(), image=self.fssp_ico, bg='#393')
        btn3.pack(side='left', fill='both', ipadx=4)

    def change_number_name(self):
        name = 'число' if self.select_znak.value == 'За' else 'числа'
        self.__number_name.set(name)

    # Табло для отображения логов
    def log_window(self):
        canvas = tk.Canvas(self, height=155, bg='#002')
        canvas.pack(side='bottom', fill=tk.X, expand=tk.YES)

        [canvas.create_line(10+x*20, 10, 10+x*20, 150, width=1, fill='#191938') for x in range(52)]
        [canvas.create_line(10, 10+y*20, 1030, 10+y*20, width=1, fill='#191938') for y in range(8)]

        canvas.create_line(20, 80, 1020, 80, width=1, fill='#FFF', arrow=tk.LAST)
        canvas.create_text(40, 70, text='Пульс', fill='#FFF')

    # Вывод на передний план фрейма
    def show_frame(self, context):
        frame = self.frames[context]
        frame.tkraise()

    # Собираем данные для request -> fssp.ru
    def get_req_data(self):
        znak = None if self.select_znak.value == 'За' else 'X'
        date = self.select_date.date
        date = None if len(date) < 9 else date
        arr = self.db.select_sql(date, znak)
        frame = self.frames[MainPage]
        frame.view_records(arr)
        frame.tkraise()

    def get_fssp_data(self):
        self.fssp.arr = self.frames[MainPage].req_array()
        if self.fssp.arr:
            self.frames[MainPage].insert_sum(self.fssp.arr)

    # CONFIG
    def get_config(self):
        self.cfg = configparser.ConfigParser()
        config = configparser.ConfigParser()
        if config.read('config.ini'):
            print('Reading config file\33[94m config.ini\33[0m -\33[93m OK\33[0m')
        else:
            print('Reading config file\33[94m config.ini\33[0m -\33[91m Fail\33[0m')
        self.cfg.add_section('OPTIONS')     # OPTIONS CONFIG
        self.cfg.set('OPTIONS', 'SAVE_RESULTS', config.get('OPTIONS', 'SAVE_RESULTS', fallback='True'))
        self.cfg.set('OPTIONS', 'RES_FILE_RENEW', config.get('OPTIONS', 'RES_FILE_RENEW', fallback='True'))
        self.cfg.set('OPTIONS', 'RES_FILE_HEAD', config.get('OPTIONS', 'RES_FILE_HEAD',
                    fallback='Время, Адрес, Участок, Реестр, Контрольная сумма, Комментарий, Задержан, Сумма штрафов'))
#       RES_FILE_HEAD = [v.strip() for v in config['OPTIONS']['RES_FILE_HEAD'].split(',')]
        self.cfg.add_section('PATH')        # PATH CONFIG
        self.cfg.set('PATH', 'DIR', config.get('PATH', 'DIR', fallback='C:\\tmp\\'))
        self.cfg.set('PATH', 'RES_FILENAME', config.get('PATH', 'RES_FILENAME', fallback='fssp.csv'))
        self.cfg.add_section('POSTGRES')  # PG_SQL CONFIG
        self.cfg.set('POSTGRES', 'HOST', config.get('POSTGRES', 'HOST', fallback='localhost'))
        self.cfg.set('POSTGRES', 'DBNAME', config.get('POSTGRES', 'DBNAME', fallback='skuns'))
        self.cfg.set('POSTGRES', 'USER', config.get('POSTGRES', 'USER', fallback='postgres'))
        self.cfg.set('POSTGRES', 'PWD', config.get('POSTGRES', 'PWD', fallback='111'))
        self.cfg.add_section('FSSP.RU')     # FSSP CONFIG
        self.cfg.set('FSSP.RU', 'PAUSE', config.get('FSSP.RU', 'PAUSE', fallback='15'))
        self.cfg.set('FSSP.RU', 'TOKEN', config.get('FSSP.RU', 'TOKEN', fallback='k51UxJdRmtyZ'))
        self.cfg.set('FSSP.RU', 'URL', config.get('FSSP.RU', 'URL', fallback='https://api-ip.fssprus.ru/api/v1.0/'))
        self.cfg.add_section('LOGS')      # LOG CONFIG
        self.cfg.set('LOGS', 'SAVE_TO_FILE', config.get('LOGS', 'SAVE_TO_FILE', fallback='True'))
        self.cfg.set('LOGS', 'LOG_LVL', config.get('LOGS', 'LOG_LVL', fallback='3'))
#       log_file_name = PATH['DIR'] + 'Logs\\fssp_' + time.strftime("%d.%m.%y", time.localtime()) + '.log'
        if not configparser.ConfigParser().read('config.ini'):
            print('Creating config file\33[94m config.ini\33[0m with default settings')
        self.save_cfg()

    def save_cfg(self):
        with open('config.ini', 'w') as cfg_file:
            self.cfg.write(cfg_file)


class MainPage(tk.Frame):
    # Фрейм главной страницы
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.tree = ttk.Treeview(self, height=10, show='headings', padding=0, selectmode='browse',
                             column=('F', 'I', 'O', 'dr', 'dt', 'adr', 'court', 'rst', 'csum', 'comm', 'jail', 'sum'),
                             displaycolumns=('dt', 'adr', 'court', 'rst', 'csum', 'comm', 'jail', 'sum'))
        # Таблица для вывода результатов
        self.tree.column('dt', width=110, anchor=tk.CENTER)
        self.tree.column('adr', width=250, anchor=tk.W)
        self.tree.column('court', width=55, anchor=tk.CENTER)
        self.tree.column('rst', width=50, anchor=tk.CENTER)
        self.tree.column('csum', width=130, anchor=tk.W)
        self.tree.column('comm', width=250, anchor=tk.CENTER, stretch=True)
        self.tree.column('jail', width=80, anchor=tk.CENTER)
        self.tree.column('sum', width=110, anchor=tk.CENTER)

        self.tree.heading('dt', text='Время')
        self.tree.heading('adr', text='Адрес')
        self.tree.heading('court', text='Участок')
        self.tree.heading('rst', text='Реестр')
        self.tree.heading('csum', text='Контрольная сумма')
        self.tree.heading('comm', text='Комментарий')
        self.tree.heading('jail', text='Задержаний')
        self.tree.heading('sum', text='Сумма взысканий')

        self.tree.pack(side='top', fill='both')

    def view_records(self, arr=()):
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in arr]

    def req_array(self):
        arr = []
        for row_id in self.tree.get_children():
            row = self.tree.set(row_id)
            add = [row['F'], row['I'], row['O'], row['dr']]
            arr.append(add)
        return arr

    def insert_sum(self, sum_array):
        for row_id in self.tree.get_children():
            row = self.tree.set(row_id)
            for res in sum_array:
                if res[0] == 1:  # Берем только физиков
                    if 'sum' not in row.keys():
                        if res[1:5] == [row['F'], row['I'], row['O'], row['dr']]:
                            self.tree.set(row_id, 'sum', res[5])


# Фрейм для страницы настроек
class SettingsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.config(bd=2, relief='groove')
        main_options = tk.Frame(self, bd=2, relief='groove')
        main_options.pack(side='left', fill='y', padx=5, pady=5)

        tk.Label(main_options, text='Postgres Settings', anchor='w').grid(row=0, column=0, columnspan=2)

        label1 = tk.Label(main_options, text=controller.cfg['POSTGRES']['HOST'])
        label1.grid(row=1, column=0)
        button1 = ttk.Button(main_options, text='Second page', command=lambda: controller.show_frame(MainPage))
        button1.grid(row=2, column=1)

        label2 = tk.Label(main_options, text='Main page')
        label2.grid(row=2, column=0)
        button2 = ttk.Button(main_options, text='Main page', command=lambda: controller.show_frame(MainPage))
        button2.grid(row=2, column=1)

        label3 = tk.Label(main_options, text='Main page')
        label3.grid(row=3, column=0)
        button3 = ttk.Button(main_options, text='Main page', command=lambda: controller.show_frame(MainPage))
        button3.grid(row=3, column=1)


class TkCombo(tk.Frame):
    """ tk ComboBox remake
        наследует фон
        to set chosen value: self.value = 0
    """
    def __init__(self, master, *args, **kwargs):
        super().__init__()
        self.__current = tk.StringVar()
        # Create main label
        self.__main = tk.Label(master, textvariable=self.__current, **kwargs, bd=2, relief='groove', cursor='hand2')
        self.__main.pack(side='left', fill='both')
        self.__bind_hover(self.__main)
        self.__values = args
        self.value = 0
        # Config main
        self.__main.bind('<Button-1>', lambda event:  self.__popup_show(**kwargs))   # When PopUp lose focus

    @property
    def value(self):
        return self.__main['text']

    @value.setter
    def value(self, index=0):
        self.__current.set(self.__values[index])

    def __popup_show(self, **kwargs):
        top = tk.Toplevel()
        top.resizable(False, False)
        top.overrideredirect(1)                # Убрать TitleBar
        x = self.__main.winfo_rootx()
        y = self.__main.winfo_rooty() + self.__main.winfo_height()
        top.geometry('+{}+{}'.format(x, y))    # Смещение окна
        top.focus_force()  # Делаем окно активным (для bind: <FocusOut>)
        # Create popup frame
        top.bind('<FocusOut>', lambda event: top.destroy())   # When PopUp lose focus
        for value in self.__values:
            val = tk.Label(top, text=value, **kwargs, bd=2, relief='ridge', cursor='hand2')
            val.pack(side='top', fill='both')
            val.bind('<Button-1>', self.__select)
            self.__bind_hover(val)

    def __select(self, event):
        self.__current.set(event.widget['text'])
        self.__main.focus_force()

    @staticmethod
    def __bind_hover(widget):
        enter_color = widget['highlightbackground']
        leave_color = widget['background']
        widget.bind('<Enter>', lambda event, bg=enter_color: widget.config(background=bg))
        widget.bind('<Leave>', lambda event, bg=leave_color: widget.config(background=bg))


if __name__ == '__main__':
    app = App()
    app.mainloop()
