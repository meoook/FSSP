"""
Version: 0.81
Author: meok

CHANGE LOG
v0.82:
    1. Adding logging
v0.81:
    1. Adding buttons behaviour when settings changes or connect DB or FSSP (threads)
    2. Config default button
v0.8: ToolBar several fixes
v0.7: Own calendar class
v0.6: Adding TreeView
v0.5: Adding ToolBar
v0.4: Adding MenuBar
v0.3:
    1. Making GUI for application
"""
import configparser
import requests
import time
import re
import psycopg2
import os
import tkinter as tk
import threading
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
        try:
            self.conn = psycopg2.connect(host=pa['host'], database=pa['dbname'], user=pa['user'], password=pa['pwd'])
            self.cur = self.conn.cursor()
        except psycopg2.Error as error:
            print('DB ERROR', error)
            self.conn = None
            self.cur = None
        else:
            print('DB CONNECTED')

    # Делаем SELECT
    def select_sql(self, date=None, znak=None):

        # Home version
        select = "SELECT upper(lastname), upper(firstname), upper(secondname), to_char(birthday, 'DD.MM.YYYY'), " \
                 "to_char(creation_date, 'DD.MM.YYYY hh24:mi:ss'), court_adr, court_numb, reestr, " \
                 "md5(concat(upper(lastname), upper(firstname), upper(secondname), to_char(birthday, 'DD.MM.YYYY'))) " \
                 "FROM fssp as v WHERE creation_date::date "
        # work version
        '''
        select = "SELECT " \
                 "upper(v.last_name), upper(v.first_name), upper(v.patronymic), to_char(v.birthdate, 'DD.MM.YYYY'), " \
                 "to_char(c.creation_date, 'DD.MM.YYYY hh24:mi:ss'), o.address, u.\"number\", " \
                 "CASE WHEN mia_check_result = 1 THEN 'МВД' ELSE 'ФССП' END, " \
                 "md5(concat(upper(v.last_name), upper(v.first_name), upper(v.patronymic), v.birthdate::date)) " \
                 "FROM visitor_violation_checks AS c " \
                 "RIGHT JOIN visitors AS v ON c.visitor_id = v.id " \
                 "RIGHT JOIN court_objects AS o ON v.court_object_id = o.id " \
                 "RIGHT JOIN court_stations AS u ON v.court_station_id = u.id " \
                 "WHERE v.court_object_id not IN (173, 174) " \
                 "AND (mia_check_result = 1 OR fssp_check_result = 1) " \
                 "AND v.creation_date::date "
        '''
        select += ">=" if znak else "="
        select += "'" + date + "'" if date else "current_date"  # Нужна проверочка - что date соответсвует формату
        select += " ORDER BY v.creation_date DESC"
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
        # App window Settings
        self.title("Проверяльщик ФССП")                    # Название
        self.geometry('+500+300')    # Смещение окна
        self.resizable(False, False)                       # Растягивается
        self.iconbitmap(self, default='.\\img\\ico.ico')   # Иконка приложения
        # Отображаемые модули\виджиты на главном фрейме
        self.menu_bar()
        self.tool_bar()
        # Табло для отображения логов
        self.log_f = tk.Text(self, height=10, bg='#001', fg='#AAA', selectbackground='#118', padx=10)
        self.log_f.pack(side='bottom', fill='both', padx=2, pady=2)
        self.log_f.mark_set('fin', '1.0')        # Load Config - надо после log_window для отображения ошибок
        self.get_config()
        # Создаем верхний фрейм, куда будем пихать другие страницы\фреймы
        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True, padx=2)
        # Загружаем фреймы
        self.frames = {}
        for F in (MainF, SettingsF):    # Список всех фреймов
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')
        # При запуске инициализируем конфиг и показываем заглавную страницу
        self.threads = []
        self.show_frame(MainF)

        self.to_log('TEST MESSAGE INFO')
        self.to_log('TEST MESSAGE WARNING', 2)
        self.to_log('TEST MESSAGE CRITICAL', 1)
        self.to_log('LOG {} HAVE DIFFERENT {}', 3, 'FUNCTION', 'PARAMETERS', c1='#44F', c2='#EE4')
        self.to_log('YOU CAN CHANGE {} AND USE {}', 3, 'COLORS', '.FORMAT', c1='#F00', c2='#FFF')
        self.to_log('test {} testing asd  asd {} testing 3 and more {} parametre {}', 3,
                    'COLORS', '.FORMAT', 'USER', 'WINDOWS', c1='#F73', c2='#37F', c3='#F0F', c4='#3F3')



    def init_connections(self):
        for x in self.threads:
            if x.is_alive():
                print('BUSY')
                return False
        print('NOT BUSY')
        thr = threading.Thread(target=self.connections)  # Поскольку в процессе есть запрос к бд thread
        self.threads.append(thr)
        thr.start()
        return True

    def connections(self):
        """ Connect to DB, Check FSSP, Check buttons - in other thread """
        self.get_config()
        self.btn_sql.config(state='disabled')
        self.btn_fssp.config(state='disabled')
        self.btn_save.config(state='disabled')
        # Вызов класса ФССП
        self.fssp = FSSP(self.cfg['FSSP.RU']['TOKEN'], self.cfg['FSSP.RU']['PAUSE'], self.cfg['FSSP.RU']['URL'])
        # Вызов класса ДБ
        self.db = DataBase({'host': self.cfg['POSTGRES']['HOST'], 'dbname': self.cfg['POSTGRES']['DBNAME'],
                            'user': self.cfg['POSTGRES']['USER'], 'pwd': self.cfg['POSTGRES']['PWD']})
        self.tool_bar_btns_chk()

    # Главное меню (полоска)
    def menu_bar(self):
        menubar = tk.Menu(self)
        # File SubMenu
        file = tk.Menu(menubar, tearoff=0)
        file.add_command(label='New', command=lambda: self.show_frame(MainF))
        file.add_command(label='Open')
        file.add_command(label='Save')
        file.add_command(label='Close')
        file.add_command(label='Options', command=lambda: self.show_frame(SettingsF))
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
        font = ('helvetica', 27)     # "Arial 24"
        # ToolBar Frame
        toolbar = tk.Frame(self, bg='#393', bd=1, relief='solid')
        toolbar.pack(side='top', fill='both', padx=2)
        self.bind('<ButtonRelease>', lambda e: self.change_number_name())     # Or check gui funct
        # ICONS
        self.settings_ico = tk.PhotoImage(file='.\\img\\setting4.png').subsample(6)
        self.home_ico = tk.PhotoImage(file='.\\img\\home.png').subsample(12)
        self.sql_ico = tk.PhotoImage(file='.\\img\\sql2.png').subsample(15)
        self.fssp_ico = tk.PhotoImage(file='.\\img\\fssp.png').subsample(8)
        self.save_ico = tk.PhotoImage(file='.\\img\\save.png').subsample(12)
        ''' ToolBar elements '''
        self.btn_s = tk.Button(toolbar, command=lambda: self.tool_bar_fbtn(), image=self.settings_ico, bg='#393')
        self.btn_s.pack(side='left', fill='both')
        self.btn_s.config(highlightbackground='#4B4')
        TkCombo.bind_hover(self.btn_s)

        select_label = tk.Label(toolbar, font=font, text='Найти нарушителей', bg='#beb', fg='#393')
        select_label.pack(side='left', fill='both')

        self.select_znak = TkCombo(toolbar, 'За', 'С',  font=font, width=2, bg='#393', highlightbackground='#4B4')

        self.select_date = DateEntry(toolbar, font=font,  bd=0, bg='#393', fg='#000', highlightbackground='#beb')
        #self.select_date.config(relief='solid', bd=1)
        self.select_date.pack(side='left', fill='both')
        CalPopup(self.select_date)
        self.select_date.date = '24.05.2019'

        self.__number_name = tk.StringVar()
        number_name = tk.Label(toolbar, font=font, textvariable=self.__number_name, bg='#beb', fg='#393')
        number_name.pack(side='left', fill='both')
        self.change_number_name()

        self.btn_sql = tk.Button(toolbar, command=self.__req_get_sql, image=self.sql_ico, bg='#393')
        self.btn_sql.pack(side='left', fill='both', ipadx=4)

        self.btn_fssp = tk.Button(toolbar, command=self.get_fssp_data, image=self.fssp_ico, bg='#393', state='disabled')
        self.btn_fssp.pack(side='left', fill='both', ipadx=4)

        self.btn_save = tk.Button(toolbar, command=self.__save_data, image=self.save_ico, bg='#393', state='disabled')
        self.btn_save.pack(side='left', fill='both', ipadx=4)

        author = tk.Label(toolbar, font=('Console', 8), text='Version: 0.82\nAuthor: meok', bg='#beb', fg='#000')
        author.pack(side='left', fill='both', expand=True)

    def tool_bar_fbtn(self, where='home'):
        if where == 'x':
            self.btn_s.config(image=self.settings_ico)
            self.btn_s.config(command=lambda: self.tool_bar_fbtn('home'))
            self.show_frame(MainF)
        else:
            self.btn_s.config(image=self.home_ico)
            self.btn_s.config(command=lambda: self.tool_bar_fbtn('x'))
            self.show_frame(SettingsF)

    def tool_bar_btns_off(self, off=True):
        state = 'disabled' if off else 'normal'
        self.btn_s.config(state=state)
        self.btn_sql.config(state=state)
        self.btn_fssp.config(state=state)
        self.btn_save.config(state=state)

    def tool_bar_btns_chk(self):
        s_fssp, s_save = self.frames[MainF].get_state()
        db_state = 'normal' if self.db.cur is not None else 'disabled'
        self.btn_s.config(state='normal')
        self.btn_sql.config(state=db_state)
        self.btn_fssp.config(state=s_fssp)
        self.btn_save.config(state=s_save)

    def change_number_name(self):
        name = 'число' if self.select_znak.value == 'За' else 'числа'
        self.__number_name.set(name)

    # Вывод на передний план фрейма
    def show_frame(self, context):
        frame = self.frames[context]
        frame.tkraise()
        self.init_connections()

    # Собираем данные для request -> fssp.ru
    def __req_get_sql(self):
        znak = None if self.select_znak.value == 'За' else 'X'
        date = self.select_date.date
        date = None if len(date) < 9 else date
        arr = self.db.select_sql(date, znak)
        frame = self.frames[MainF]
        frame.view_records(arr)
        frame.tkraise()
        self.tool_bar_btns_chk()

    def get_fssp_data(self):
        x = self
        self.tool_bar_btns_off()

        def callback():
            x.fssp.arr = x.frames[MainF].req_array()   # When set arr - the request to FSSP begins
            if x.fssp.arr:
                x.frames[MainF].insert_sum(x.fssp.arr)
            x.tool_bar_btns_chk()
        thr = threading.Thread(target=callback)          # Поскольку в процессе есть sleep то пускаем в другой thread
        thr.start()

    def __save_data(self):
        print('SAVING ))')
        pass

    def get_config(self):
        self.cfg = configparser.ConfigParser()
        config = configparser.ConfigParser()
        if config.read('config.ini'):
            self.to_log('Reading config file {} - {}', 3, 'config.ini', 'OK', c1='#CC0', c2='#3B3')
        else:
            self.to_log('Reading config file {} - {}', 3, 'config.ini', 'Fail', c1='#CC0', c2='#C33')
        self.cfg.add_section('OPTIONS')     # OPTIONS CONFIG
        self.cfg.set('OPTIONS', 'SAVE_TO_FILE', config.get('OPTIONS', 'SAVE_TO_FILE', fallback='ON'))
        self.cfg.set('OPTIONS', 'FILE_RENEW', config.get('OPTIONS', 'FILE_RENEW', fallback='ON'))
        self.cfg.set('OPTIONS', 'SAVE_SQLITE', config.get('OPTIONS', 'SAVE_SQLITE', fallback='OFF'))
        self.cfg.add_section('PATH')        # PATH CONFIG
        self.cfg.set('PATH', 'DIR', config.get('PATH', 'DIR', fallback='C:\\tmp\\'))
        self.cfg.set('PATH', 'RES_FILENAME', config.get('PATH', 'RES_FILENAME', fallback='fssp.csv'))
        self.cfg.add_section('POSTGRES')    # PG_SQL CONFIG
        self.cfg.set('POSTGRES', 'HOST', config.get('POSTGRES', 'HOST', fallback='localhost'))
        self.cfg.set('POSTGRES', 'DBNAME', config.get('POSTGRES', 'DBNAME', fallback='skuns'))
        self.cfg.set('POSTGRES', 'USER', config.get('POSTGRES', 'USER', fallback='postgres'))
        self.cfg.set('POSTGRES', 'PWD', config.get('POSTGRES', 'PWD', fallback='111'))
        self.cfg.add_section('FSSP.RU')     # FSSP CONFIG
        self.cfg.set('FSSP.RU', 'PAUSE', config.get('FSSP.RU', 'PAUSE', fallback='15'))
        self.cfg.set('FSSP.RU', 'TOKEN', config.get('FSSP.RU', 'TOKEN', fallback='k51UxJdRmtyZ'))
        self.cfg.set('FSSP.RU', 'URL', config.get('FSSP.RU', 'URL', fallback='https://api-ip.fssprus.ru/api/v1.0/'))
        self.cfg.add_section('LOGS')        # LOG CONFIG
        self.cfg.set('LOGS', 'SAVE', config.get('LOGS', 'SAVE', fallback='ON'))
        self.cfg.set('LOGS', 'LVL', config.get('LOGS', 'LVL', fallback='3'))
        self.log_file = self.cfg.get('PATH', 'DIR') + 'Logs\\fssp_' + time.strftime("%d.%m.%y", time.localtime())+'.log'
        if not configparser.ConfigParser().read('config.ini'):
            self.to_log('Creating config file {} with default settings', 3, 'config.ini', c1='#FF0')
        self.save_cfg()

    def save_cfg(self):
        with open('config.ini', 'w') as cfg_file:
            self.cfg.write(cfg_file)

    # Записать сообщение в лог файл
    def to_log(self, msg: str, deep_lvl: int = 3, *args, **kwargs):
        next_index = self.log_f.index('fin')
        next_row_n = next_index.split('.')[0]
        if msg is False:
            msg = 'Try to put empty message in log'
            deep_lvl = 1
        if deep_lvl == 1:
            echo = '\x1b[31m[CRIT]\x1b[0m ' + msg
            msg = '[CRIT] ' + msg
            lvl_color = '#F44'
        elif deep_lvl == 2:
            echo = '\x1b[33m[FAIL]\x1b[0m ' + msg
            msg = '[FAIL] ' + msg
            lvl_color = '#F73'
        else:
            echo = '\x1b[94m[INFO]\x1b[0m ' + msg
            msg = '[INFO] ' + msg
            lvl_color = '#37F'
        msg = time.strftime("%d.%m.%y %H:%M:%S", time.localtime()) + ' ' + msg
        print(echo.format(*args))
        msg_copy = msg
        msg = msg.format(*args)
        self.log_f.insert(next_index, "{}\n".format(msg))
        self.log_f.see(tk.END)
        self.log_f.tag_add(next_index + 'time', next_index, next_row_n + '.17')
        self.log_f.tag_config(next_index + 'time', foreground='#AA5')
        self.log_f.tag_add(next_index + 'err_lvl', next_row_n + '.18', next_row_n + '.24')
        self.log_f.tag_config(next_index + 'err_lvl', foreground=lvl_color)
        if '{}' in msg_copy:
            if kwargs:
                colors = [str(c) for c in kwargs.values()]
                a_lens = [len(str(string)) for string in args]
                positions = [pos for pos, char in enumerate(msg_copy) if char == '{']
                args_lens = 0
                for i in range(len(positions)):
                    start = positions[i] + args_lens
                    end = next_row_n + '.' + str(start + a_lens[i])
                    start = next_row_n + '.' + str(start)
                    self.log_f.tag_add(start, start, end)
                    self.log_f.tag_config(start, foreground=colors[i])
                    args_lens += a_lens[i] - 2  # 2 символа это {}
        '''
        if self.cfg['LOGS']['SAVE']:
            pass

            if self.cfg['LOGS']['LVL'] >= deep_lvl:
                with open(LOG_FILE_NAME, "a") as filo:
                    filo.write(msg + '\n')
        '''


class MainF(tk.Frame):
    # Фрейм главной страницы
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        #self.config(bd=2, relief='groove')

        self.tree = ttk.Treeview(self, height=12, show='headings', padding=0, selectmode='browse',
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
                    if 'sum' not in row.keys():  # Могут быть повторы, тем самым исключаем
                        if res[1:5] == [row['F'], row['I'], row['O'], row['dr']]:
                            self.tree.set(row_id, 'sum', res[5])

    def get_state(self):
        state_fssp = 'normal' if len(self.tree.get_children()) > 0 else 'disabled'
        state_save = 'disabled'
        if self.tree.get_children():
            state_save = 'normal' if 'sum' in self.tree.set(self.tree.get_children()[0]).keys() else 'disabled'
        return state_fssp, state_save


class SettingsF(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.cc = controller
        font = ('Verdana', 12)    # Times/Verdana/Lucida/Tempus Sans ITC/Console/Courier/Helvetica
        font_big = ('Tempus Sans ITC', 16, 'bold')
        self.config(bd=2, relief='groove')
        # StringVar Setting
        self.o_m_save = tk.StringVar()
        self.o_m_renew = tk.StringVar()
        self.o_m_sqlite = tk.StringVar()
        self.o_p_dir = tk.StringVar()
        self.o_p_name = tk.StringVar()
        self.o_f_pause = tk.StringVar()
        self.o_f_token = tk.StringVar()
        self.o_f_url = tk.StringVar()
        self.o_l_save = tk.StringVar()
        self.o_l_lvl = tk.StringVar()
        self.o_pg_host = tk.StringVar()
        self.o_pg_name = tk.StringVar()
        self.o_pg_user = tk.StringVar()
        self.o_pg_pass = tk.StringVar()

        self.settings_get()
        self.trace()

        # ======== MAIN OPTIONS =========================================
        opt_main = tk.Frame(self, bd=2, relief='groove')
        opt_main.grid(row=0, column=0, padx=5, ipadx=0, pady=5, ipady=5, sticky='WEN')
        tk.Label(opt_main, text='Main Settings', font=font_big).grid(row=0, column=0, columnspan=2)
        tk.Label(opt_main, text='Save results', anchor='w', width=15).grid(row=1, column=0, sticky='EW', padx=5)
        tk.Button(opt_main, textvariable=self.o_m_save, width=3, command=lambda: self.change(self.o_m_save, 'b')).grid(row=1, column=1)
        tk.Label(opt_main, text='Renew file', anchor='w').grid(row=2, column=0, sticky='EW', padx=5)
        tk.Button(opt_main, textvariable=self.o_m_renew, width=3, command=lambda: self.change(self.o_m_renew, 'b')).grid(row=2, column=1)
        tk.Label(opt_main, text='Save to SQLite', anchor='w').grid(row=3, column=0, sticky='EW', padx=5)
        tk.Button(opt_main, textvariable=self.o_m_sqlite, width=3, command=lambda: self.change(self.o_m_sqlite, 'b')).grid(row=3, column=1)
        # ======== LOGS OPTIONS =========================================
        opt_logs = tk.Frame(self, bd=2, relief='groove')
        opt_logs.grid(row=2, column=0, padx=5, ipadx=5, pady=5, ipady=5, sticky='WENS')
        tk.Label(opt_logs, text='Logs Settings', font=font_big).grid(row=0, column=0, columnspan=2)
        tk.Label(opt_logs, text='Save logs', anchor='w', width=15).grid(row=1, column=0, sticky='EW', padx=5)
        tk.Button(opt_logs, textvariable=self.o_l_save, width=3, command=lambda: self.change(self.o_l_save, 'b')).grid(row=1, column=1)
        tk.Label(opt_logs, text='Log level', anchor='w').grid(row=2, column=0, sticky='EW', padx=5)
        tk.Button(opt_logs, textvariable=self.o_l_lvl, width=3, command=lambda: self.change(self.o_l_lvl, 'lvl')).grid(row=2, column=1)
        # ======== FSSP OPTIONS =========================================
        opt_fssp = tk.Frame(self, bd=2, relief='groove', padx=5)
        opt_fssp.grid(row=0, column=1, padx=0, ipadx=0, pady=5, ipady=5, columnspan=2, sticky='WEN')
        tk.Label(opt_fssp, text='FSSP Settings', font=font_big).grid(row=0, column=0, columnspan=3)
        tk.Label(opt_fssp, text='API URL', anchor='w').grid(row=1, column=0, sticky='EW')
        tk.Entry(opt_fssp, textvariable=self.o_f_url, width=30).grid(row=1, column=1, columnspan=2)
        tk.Label(opt_fssp, text='TOKEN', anchor='w').grid(row=2, column=0, sticky='EW')
        tk.Entry(opt_fssp, textvariable=self.o_f_token).grid(row=2, column=1, sticky='EW')
        tk.Button(opt_fssp, text='CHECK', width=6).grid(row=2, column=2, rowspan=2, sticky='NS')
        tk.Label(opt_fssp, text='PAUSE', anchor='w').grid(row=3, column=0, sticky='EW')
        tk.Entry(opt_fssp, textvariable=self.o_f_pause).grid(row=3, column=1, sticky='EW')
        # ======== PATH OPTIONS =====================================
        opt_path = tk.Frame(self, bd=2, relief='groove', padx=5)
        opt_path.grid(row=2, column=1, padx=5, ipadx=0, pady=5, ipady=5, sticky='WEN')
        tk.Label(opt_path, text='Path Settings', font=font_big).grid(row=0, column=0, columnspan=2)
        tk.Label(opt_path, text='Directory', anchor='w').grid(row=1, column=0, sticky='EW')
        tk.Entry(opt_path, textvariable=self.o_p_dir).grid(row=1, column=1)
        tk.Label(opt_path, text='result file', anchor='w').grid(row=2, column=0, sticky='EW')
        tk.Entry(opt_path, textvariable=self.o_p_name).grid(row=2, column=1)
        # ======== Postgres OPTIONS =====================================
        opt_pg = tk.Frame(self, bd=2, relief='groove', padx=5)
        opt_pg.grid(row=0, column=3, padx=5, ipadx=0, pady=5, ipady=5, sticky='WEN')
        tk.Label(opt_pg, text='Postgres Settings', font=font_big).grid(row=0, column=0, columnspan=2)
        tk.Label(opt_pg, text='Hostname', anchor='w').grid(row=1, column=0, sticky='EW')
        tk.Entry(opt_pg, textvariable=self.o_pg_host, width=12).grid(row=1, column=1)
        tk.Label(opt_pg, text='DB name', anchor='w').grid(row=2, column=0, sticky='EW')
        tk.Entry(opt_pg, textvariable=self.o_pg_name, width=12).grid(row=2, column=1)
        tk.Label(opt_pg, text='DB user', anchor='w').grid(row=3, column=0, sticky='EW')
        tk.Entry(opt_pg, textvariable=self.o_pg_user, width=12).grid(row=3, column=1)
        tk.Label(opt_pg, text='Password', anchor='w').grid(row=4, column=0, sticky='EW')
        tk.Entry(opt_pg, textvariable=self.o_pg_pass, width=12, show='*').grid(row=4, column=1)
        # ======== RESTORE DEFAULTS BUTTON =====================================
        btn_save = tk.Button(self, bd=2, padx=5, font=font_big, text='DEFAULTS', command=self.defaults)
        btn_save.grid(row=2, column=3, padx=5, ipadx=0, pady=5, ipady=5, rowspan=2, sticky='WEN')

    def settings_get(self):
        self.o_m_save.set(self.cc.cfg['OPTIONS']['SAVE_TO_FILE'])
        self.o_m_renew.set(self.cc.cfg['OPTIONS']['FILE_RENEW'])
        self.o_m_sqlite.set(self.cc.cfg['OPTIONS']['SAVE_SQLITE'])

        self.o_p_dir.set(self.cc.cfg['PATH']['DIR'])
        self.o_p_name.set(self.cc.cfg['PATH']['RES_FILENAME'])

        self.o_f_token.set(self.cc.cfg['FSSP.RU']['TOKEN'])
        self.o_f_url.set(self.cc.cfg['FSSP.RU']['URL'])
        self.o_f_pause.set(self.cc.cfg['FSSP.RU']['PAUSE'])

        self.o_l_save.set(self.cc.cfg['LOGS']['SAVE'])
        self.o_l_lvl.set(self.cc.cfg['LOGS']['LVL'])

        self.o_pg_host.set(self.cc.cfg['POSTGRES']['HOST'])
        self.o_pg_name.set(self.cc.cfg['POSTGRES']['DBNAME'])
        self.o_pg_user.set(self.cc.cfg['POSTGRES']['USER'])
        self.o_pg_pass.set(self.cc.cfg['POSTGRES']['PWD'])

    def settings_set(self, *args):
        self.cc.cfg.set('OPTIONS', 'SAVE_TO_FILE', self.o_m_save.get())
        self.cc.cfg.set('OPTIONS', 'FILE_RENEW', self.o_m_renew.get())
        self.cc.cfg.set('OPTIONS', 'SAVE_SQLITE', self.o_m_sqlite.get())

        self.cc.cfg.set('PATH', 'DIR', self.o_p_dir.get())
        self.cc.cfg.set('PATH', 'RES_FILENAME', self.o_p_name.get())

        self.cc.cfg.set('FSSP.RU', 'URL', self.o_f_url.get())
        self.cc.cfg.set('FSSP.RU', 'TOKEN', self.o_f_token.get())
        self.cc.cfg.set('FSSP.RU', 'PAUSE', self.o_f_pause.get())

        self.cc.cfg.set('LOGS', 'SAVE', self.o_l_save.get())
        self.cc.cfg.set('LOGS', 'LVL', self.o_l_lvl.get())

        self.cc.cfg.set('POSTGRES', 'HOST', self.o_pg_host.get())
        self.cc.cfg.set('POSTGRES', 'DBNAME', self.o_pg_name.get())
        self.cc.cfg.set('POSTGRES', 'USER', self.o_pg_user.get())
        self.cc.cfg.set('POSTGRES', 'PWD', self.o_pg_pass.get())

        self.cc.save_cfg()
        self.cc.init_connections()

    def change(self, var, typo='b'):
        v = var.get()
        if typo == 'b':
            var.set('ON') if v == 'OFF' else var.set('OFF')
        elif typo == 'lvl':
            var.set('1') if v == '3' else var.set('2') if v == '1' else var.set('3')
        self.settings_set()

    def defaults(self):
        self.trace(False)
        self.cc.cfg.remove_section('OPTIONS')
        self.cc.cfg.remove_section('PATH')
        self.cc.cfg.remove_section('POSTGRES')
        self.cc.cfg.remove_section('FSSP.RU')
        self.cc.cfg.remove_section('LOGS')
        self.cc.save_cfg()
        self.cc.get_config()
        self.settings_get()
        self.trace()

    def trace(self, on=True):   # trace_vdelete
        if on:
            self.o_p_dir.trace("w", self.settings_set)
            self.o_p_name.trace("w", self.settings_set)
            self.o_f_pause.trace("w", self.settings_set)
            self.o_f_token.trace("w", self.settings_set)
            self.o_f_url.trace("w", self.settings_set)
            self.o_pg_host.trace("w", self.settings_set)
            self.o_pg_name.trace("w", self.settings_set)
            self.o_pg_user.trace("w", self.settings_set)
            self.o_pg_pass.trace("w", self.settings_set)
        else:
            self.trace_clear(self.o_p_dir)
            self.trace_clear(self.o_p_name)
            self.trace_clear(self.o_f_pause)
            self.trace_clear(self.o_f_token)
            self.trace_clear(self.o_f_url)
            self.trace_clear(self.o_pg_host)
            self.trace_clear(self.o_pg_name)
            self.trace_clear(self.o_pg_user)
            self.trace_clear(self.o_pg_pass)

    @staticmethod
    def trace_clear(str_var):
        for t in str_var.trace_vinfo():
            str_var.trace_vdelete(*t)


class TkCombo(tk.Frame):
    """ tk ComboBox remake
        наследует фон
        to set chosen value: self.value = 0
    """
    def __init__(self, master, *args, **kwargs):
        super().__init__()
        self.__current = tk.StringVar()
        # Create main label
        self.__main = tk.Label(master, textvariable=self.__current, **kwargs, bd=2, relief='raised', cursor='hand2')
        self.__main.pack(side='left', fill='both', padx=3, ipadx=5)
        self.bind_hover(self.__main)
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
            val = tk.Label(top, text=value, **kwargs, bd=1, relief='ridge', cursor='hand2')
            val.pack(side='top', fill='both', ipadx=5, padx=1)
            val.bind('<Button-1>', self.__select)
            self.bind_hover(val)

    def __select(self, event):
        self.__current.set(event.widget['text'])
        self.__main.focus_force()

    @staticmethod
    def bind_hover(widget):
        enter_color = widget['highlightbackground']
        leave_color = widget['background']
        widget.bind('<Enter>', lambda event, bg=enter_color: widget.config(background=bg))
        widget.bind('<Leave>', lambda event, bg=leave_color: widget.config(background=bg))


if __name__ == '__main__':
    app = App()
    app.mainloop()
