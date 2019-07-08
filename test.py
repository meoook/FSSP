import configparser
import requests
import time
import re
import psycopg2
import os
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry

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
class Gui(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # Отобразить встроенные стили
        style = ttk.Style()
        print(style.theme_names())
        style.theme_use('vista')
        print(style.element_names())

        # App window Settings
        self.title("Проверяльщик ФССП")                    # Название
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
        container.pack(side='top', fill='both', expand=True)
        # Загружаем фреймы
        self.frames = {}
        for F in (MainPage, SettingsPage):    # Список всех фреймов
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')
        # Подключаемся к ДБ
        self.db = DataBase({'host': self.cfg['POSTGRES']['HOST'], 'dbname': self.cfg['POSTGRES']['DBNAME'],
                            'user': self.cfg['POSTGRES']['USER'], 'pwd': self.cfg['POSTGRES']['PWD']})
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
        toolbar = ttk.Frame(self)
        toolbar.pack(side='top', fill=tk.X)

        font = ('helvetica', 27)     # "Arial 24"
        self.settings = tk.PhotoImage(file='.\\img\\settings.png')
        self.play = tk.PhotoImage(file='.\\img\\play.png')
        btn1 = ttk.Button(toolbar, command=lambda: self.show_frame(SettingsPage), image=self.settings)
        btn1.pack(side='left')

        self.sep = ttk.Separator(toolbar, orient="vertical", style="Line.TSeparator").pack(side="left", fill="y", padx=3, pady=5)  # vertical\horizontal

        select_label = ttk.Label(toolbar, text='Найти нарушителей', relief=tk.RIDGE)
        select_label.config(font=font)
        select_label.pack(side='left')

        ttk.Separator(toolbar, orient="vertical", style="Line.TSeparator").pack(side="left", fill="y", padx=3, pady=5)  # vertical\horizontal

        # STYLE STYLE STYLE :)
        st = ttk.Style()
        st.map("C.TButton",
               foreground=[('pressed', 'red'), ('active', 'green')],
               background=[('pressed', '!disabled', 'black'), ('active', 'white')],
               relief=[('pressed', '!disabled', 'sunken')])
        st.configure("C.TButton", padding=(0, 0, 0, 0))

        st.configure("Line.TSeparator", background="#fff")

        st.theme_settings("vista", {
            "TCombobox": {"configure": {"padding": 0},
                        "map": {"background": [("active", "green2"), ("!disabled", "green4"), ("selected", "black")],
                                "fieldbackground": [("!disabled", "green3")],
                                "foreground": [("focus", "OliveDrab1"), ("!disabled", "black")],
                                "activeforeground": [('selected', 'black')],
                                "relief": [('pressed', '!disabled', 'sunken')]}
                        }})

        print(st.layout('TCombobox'))
        print(st.element_options('Entry.padding'))
        # END STYLE

        self.select_znak = ttk.Combobox(toolbar, values=[u'За', u'С'], width=3)
        self.select_znak.config(font=font)
        self.select_znak.current(0)
        self.select_znak.pack(side='left')

        ttk.Separator(toolbar, orient="vertical", style="Line.TSeparator").pack(side="left", fill="y", padx=3, pady=5)  # vertical\horizontal

        self.select_date = DateEntry(toolbar, width=9,
                                     borderwidth=1,
                                     locale='ru_RU',
                                     font=font,
                                     background='#AAA',
                                     foreground='#000',
                                     bordercolor='#000',
                                     selectbackground='#090',
                                     selectforeground='#AFA',
                                     normalbackground='#CCC',
                                     normalforeground='#111',
                                     othermonthbackground='#AAA',
                                     othermonthforeground='#222',
                                     othermonthwebackground='#666',
                                     othermonthweforeground='#111',
                                     weekendbackground='#888',
                                     weekendforeground='#111',
                                     headersbackground='#EEE',
                                     headersforeground='#666', style='C.TButton')
        self.select_date.pack(side='left', ipadx=0)
        # DEBUG
        self.select_date.delete(0, tk.END)
        self.select_date.insert(0, '24.05.2019')

        ttk.Separator(toolbar, orient="vertical", style="Line.TSeparator").pack(side="left", fill="y", padx=3, pady=5)  # vertical\horizontal

        select_label2 = ttk.Label(toolbar, text='число', relief=tk.RIDGE)
        select_label2.config(font=font)
        select_label2.pack(side='left')

        ttk.Separator(toolbar, orient="vertical", style="Line.TSeparator").pack(side="left", fill="y", padx=3, pady=5)  # vertical\horizontal

        btn2 = ttk.Button(toolbar, command=lambda: self.get_req_data(), image=self.play)
        btn2.pack(side=tk.LEFT)

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
        znak = None if self.select_znak.get() == 'За' else 'X'
        date = self.select_date.get()
        date = None if len(date) < 9 else date  # '24.05.2019'
        arr = self.db.select_sql(date, znak)
        frame = self.frames[MainPage]
        frame.view_records(arr)
        frame.tkraise()

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
        self.cfg.set('FSSP.RU', 'BASE_URL', config.get('FSSP.RU', 'BASE_URL',
                                                       fallback='https://api-ip.fssprus.ru/api/v1.0/'))
        self.cfg.set('FSSP.RU', 'GROUP_URL', config.get('FSSP.RU', 'GROUP_URL', fallback='search/group'))
        self.cfg.set('FSSP.RU', 'STATUS_URL', config.get('FSSP.RU', 'STATUS_URL', fallback='status'))
        self.cfg.set('FSSP.RU', 'RESULT_URL', config.get('FSSP.RU', 'RESULT_URL', fallback='result'))
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


# Фрейм главной страницы
class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.tree = ttk.Treeview(self, height=10, show='headings', padding=0, selectmode='browse',
                                 column=('n1', 'n2', 'd3', 'dr', 'dt', 'adr', 'court', 'rst', 'csum', 'comm', 'jail', 'sum'),
                                 displaycolumns=('dt', 'adr', 'court', 'rst', 'csum', 'comm', 'jail', 'sum'))
        self.show_tree()

    # Таблица для вывода результатов
    def show_tree(self):

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

        self.tree.pack(side='top')

    def view_records(self, arr=()):
        print('Refresh Tree view', arr)
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in arr]


# Фрейм для страницы настроек
class SettingsPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        main_options = tk.Frame(self)
        main_options.pack(side='left', fill=tk.Y)

        pg_options = tk.Frame(self)
        pg_options.pack(side='left', fill=tk.Y)

        label = tk.Label(main_options, text='Second page')
        label.pack(side='top')
        button = ttk.Button(main_options, text='Main page', command=lambda: controller.show_frame(MainPage))
        button.pack(side='top')

        label2 = tk.Label(pg_options, text='Second page')
        label2.pack(side='left')
        button2 = ttk.Button(pg_options, text='Main page', command=lambda: controller.show_frame(MainPage))
        button2.pack(side='left')


if __name__ == '__main__':
    app = Gui()
    app.mainloop()
