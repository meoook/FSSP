"""
Version: 0.81
Author: meok

CHANGE LOG
TO DO: CHECK PATH
v0.9.1: Colors in logger
v0.9:   Adding logging
v0.8:   Adding buttons behaviour when settings changes or connect DB or FSSP (threads)
        Config default button
v0.8:   ToolBar several fixes
v0.7:   Own calendar class
v0.6:   Adding TreeView
v0.5:   Adding ToolBar
v0.4:   Adding MenuBar
v0.3:
    1. Making GUI for application
"""
import configparser
import time
import re
import os
import tkinter as tk
import threading
from tkinter import ttk
from myCal import DateEntry, CalPopup
from my_database import DbLocal, DataBase
from fssp import FSSP
from my_colors import Color


# Основной класс программы
class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # App window Settings
        self.title("Проверяльщик ФССП")  # Название
        self.geometry('+500+300')  # Смещение окна
        self.resizable(False, False)  # Растягивается
        self.iconbitmap(self, default='.\\img\\ico.ico')  # Иконка приложения
        # Отображаемые модули\виджиты на главном фрейме
        self.menu_bar()
        self.tool_bar()
        # Табло для отображения логов
        self.log_f = tk.Text(self, height=12, bg='#001', fg='#AAA', selectbackground='#118', padx=10)
        self.log_f.pack(side='bottom', fill='both', padx=2, pady=2)
        self.log_f.mark_set('fin', '1.0')  # Делаем метку для прокрутки\вставки
        # Провереям конфиг и пути - (пути наверное не нужно)
        self.chk_paths()
        # self.db = DbLocal()
        # Создаем верхний фрейм, куда будем пихать другие страницы\фреймы
        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True, padx=2)
        # Загружаем фреймы
        self.frames = {}
        for F in (MainF, SettingsF):  # Список всех фреймов
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')
        # При запуске инициализируем конфиг и показываем заглавную страницу
        self.__threads = []
        self.__show_frame(MainF)

    # Проверка всех путей like __init__ ; сделать через try - вдруг прав нет
    def chk_paths(self):
        cur_dir = os.getcwd() + '\\'
        self.get_config()
        self.__to_log("Application directory: {}", 3, cur_dir)
        # Проверием структуру файлов\папок
        if self.cfg['OPTIONS']['SAVE_TO_FILE'] == 'ON' or self.cfg['LOGS']['SAVE'] == 'ON':
            self.__to_log('Checking folders structure...')
        else:
            self.__to_log('No files will be used {}.', 3, 'Echo mode', c=Color.inf)
            return False
        # Если логирование включено
        if self.cfg['LOGS']['SAVE'] == 'ON':
            if os.path.isdir('Logs'):  # Проверка папки с логами
                self.__to_log('Log folder {} exist - {}', 3, cur_dir + 'Logs', 'OK', c1=Color.inf, c2=Color.ok)
            else:
                try:
                    os.makedirs('Logs')
                    self.__to_log('Log folder {} created - {}', 3, cur_dir + 'Logs', 'OK', c1=Color.inf, c2=Color.ok)
                except Exception as e:
                    self.__to_log('Log folder {} creating - {} Err:{}', 1,
                                  cur_dir + 'Logs', 'fail', e, c1=Color.inf, c2=Color.err, c3=Color.info)
                    self.__to_log('Set {} = {}', 1, 'LOG_TO_FILE', 'False', c1=Color.inf, c2=Color.fail)
                    self.cfg.set('LOGS', 'SAVE', 'OFF')
        if self.cfg['LOGS']['SAVE'] == 'ON':
            if os.path.isfile(self.log_file):  # Проверка файла логов
                print('Log file\33[93m', cur_dir + self.log_file, '\33[0mexist - \33[32mOK\33[0m')
            else:
                try:
                    filo = open(self.log_file, "w")
                    filo.write(time.strftime("%d.%m.%y %H:%M:%S", time.localtime()) +
                               ' [INFO] Created file log ' + cur_dir + self.log_file + '\n')
                    filo.close()
                    print('Log file\33[93m', cur_dir + self.log_file, '\33[0mcreated - \33[32mOK\33[0m')
                except Exception as e:
                    print('Log file\33[93m', cur_dir + self.log_file, '\33[0mcreating - \33[91mfail.', e, '\33[0m')
                    print('\33[91mSet LOG_TO_FILE = False\33[0m')
                    self.cfg.set('LOGS', 'SAVE', 'OFF')
        # Проверием папки для файла с результатами
        if self.cfg['OPTIONS']['SAVE_TO_FILE'] == 'ON':
            if os.path.isdir(self.cfg['PATH']['DIR']):  # Проверка основной папки
                print('Main folder\33[93m', self.cfg['PATH']['DIR'], '\33[0mexist - \33[32mOK\33[0m')
            else:
                try:
                    os.makedirs(self.cfg['PATH']['DIR'])
                    print('Main folder\33[93m', self.cfg['PATH']['DIR'], '\33[0m created - \33[32mOK\33[0m')
                except Exception as e:
                    print('Main folder\33[93m', self.cfg['PATH']['DIR'], '\33[0m creating - \33[91mfail.', e, '\33[0m')
                    print('\33[91mSet SAVE_RESULT = False\33[0m')
                    self.cfg.set('OPTIONS', 'SAVE_TO_FILE', 'OFF')
                    return False
        else:
            print('No save file will be used.\33[0m')
            return False
        # Создаем файл с результатами
        if self.cfg['OPTIONS']['SAVE_TO_FILE'] == 'ON':
            res_file_path = self.cfg['PATH']['DIR'] + self.cfg['PATH']['RES_FILENAME']
            if not os.path.isfile(res_file_path) or self.cfg['OPTIONS']['FILE_RENEW'] == 'ON':
                try:
                    file_head = ['Время', 'Адрес', 'Участок', 'Реестр', 'Контрольная сумма', 'Комментарий',
                                 'Задержан', 'Сумма штрафов']
                    filo = open(res_file_path, "w")
                    filo.write(";".join(file_head) + '\n')
                    filo.close()
                    print("Result file\33[93m", res_file_path, '\33[0mcreated - \33[32mOK\33[0m')
                except IOError as e:
                    print('Result file:\33[93m', res_file_path, '\33[0mcreating - \33[91mfail.', e, '\33[0m')
                    print('\33[93mSet SAVE_RESULT = False\33[0m')
                    self.cfg.set('OPTIONS', 'SAVE_TO_FILE', 'OFF')
            else:
                print('Result file\33[93m', res_file_path, '\33[0mexist - \33[32mOK\33[0m')
        return True

    def init_connections(self):
        for x in self.__threads:
            if x.is_alive():
                self.__to_log('Thread is busy. Try connect later.', 3)
                return False
        self.__to_log('Thread free. Trying connections...', 3)
        thr = threading.Thread(target=self.connections)  # Поскольку в процессе есть запрос к бд thread
        self.__threads.append(thr)
        thr.start()
        return True

    def connections(self):
        """ Connect to DB, Check FSSP, Check buttons - in other thread """
        self.get_config()
        db = DbLocal()
        print(db.visits)
        # Вызов класса ФССП
        fssp = FSSP(self.cfg['FSSP.RU']['TOKEN'], self.cfg['FSSP.RU']['PAUSE'], self.cfg['FSSP.RU']['URL'],
                         self.__to_log)
        # Вызов класса ДБ
        db_pg = DataBase({'host': self.cfg['POSTGRES']['HOST'], 'dbname': self.cfg['POSTGRES']['DBNAME'],
                          'user': self.cfg['POSTGRES']['USER'], 'pwd': self.cfg['POSTGRES']['PWD']}, self.__to_log)
        db.visits = db_pg.select_sql(db.visits[4])  # Select visits and then insert in local DB
        db_pg.close()
        fssp.arr = db.data  # Request to FSSP. db.data = array
        for x in fssp.arr:
            db.data = ('sum', *x[1:5], time.strftime("%Y-%m-%d", time.localtime()), x[5])
        self.frames[MainF].view_records(db.table)

    def menu_bar(self):
        menubar = tk.Menu(self)
        # File SubMenu
        file = tk.Menu(menubar, tearoff=0)
        file.add_command(label='New', command=lambda: self.__show_frame(MainF))
        file.add_command(label='Open')
        file.add_command(label='Save')
        file.add_command(label='Close')
        file.add_command(label='Options', command=lambda: self.__show_frame(SettingsF))
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

    def tool_bar(self):
        font = ('helvetica', 27)  # "Arial 24"
        # ToolBar Frame
        toolbar = tk.Frame(self, bg='#393', bd=1, relief='solid')
        toolbar.pack(side='top', fill='both', padx=2)
        # ICONS
        self.settings_ico = tk.PhotoImage(file='.\\img\\setting4.png').subsample(6)
        self.home_ico = tk.PhotoImage(file='.\\img\\home.png').subsample(12)
        self.sql_ico = tk.PhotoImage(file='.\\img\\sql2.png').subsample(15)
        self.fssp_ico = tk.PhotoImage(file='.\\img\\fssp.png').subsample(8)
        self.save_ico = tk.PhotoImage(file='.\\img\\save.png').subsample(12)
        ''' ToolBar elements '''
        self.btn_s = tk.Button(toolbar, command=lambda: self.__tool_bar_fbtn(), image=self.settings_ico, bg='#393')
        self.btn_s.pack(side='left', fill='both')
        self.btn_s.config(highlightbackground='#4B4')
        self.bind_hover(self.btn_s)

        select_label = tk.Label(toolbar, font=font, text='Найти нарушителей', bg='#beb', fg='#393')
        select_label.pack(side='left', fill='both')

        self.select_date = DateEntry(toolbar, font=font, bd=0, bg='#393', fg='#000', highlightbackground='#beb')
        # self.select_date.config(relief='solid', bd=1)
        self.select_date.pack(side='left', fill='both')
        CalPopup(self.select_date)

        self.btn_save = tk.Button(toolbar, command=self.__save_data, image=self.save_ico, bg='#393', state='disabled')
        self.btn_save.pack(side='left', fill='both', ipadx=4)

        author = tk.Label(toolbar, font=('Console', 8), text='Version: 0.82\nAuthor: meok', bg='#beb', fg='#000')
        author.pack(side='left', fill='both', expand=True)

    def __tool_bar_fbtn(self, where='home'):
        if where == 'x':
            self.btn_s.config(image=self.settings_ico)
            self.btn_s.config(command=lambda: self.__tool_bar_fbtn('home'))
            self.__show_frame(MainF)
        else:
            self.btn_s.config(image=self.home_ico)
            self.btn_s.config(command=lambda: self.__tool_bar_fbtn('x'))
            self.__show_frame(SettingsF)

    def __show_frame(self, context):  # Вывод на передний план фрейма
        frame = self.frames[context]
        frame.tkraise()
        self.init_connections()

    def __save_data(self):
        print('SAVING ))')
        pass

    def get_config(self):
        self.cfg = configparser.ConfigParser()
        config = configparser.ConfigParser()
        if config.read('config.ini'):
            self.__to_log('Reading config file {} - {}', 3, 'config.ini', 'OK', c1=Color.inf, c2=Color.ok)
        else:
            self.__to_log('Reading config file {} - {}', 1, 'config.ini', 'Fail', c1=Color.inf, c2=Color.fail)
        self.cfg.add_section('OPTIONS')  # OPTIONS CONFIG
        self.cfg.set('OPTIONS', 'SAVE_TO_FILE', config.get('OPTIONS', 'SAVE_TO_FILE', fallback='ON'))
        self.cfg.set('OPTIONS', 'FILE_RENEW', config.get('OPTIONS', 'FILE_RENEW', fallback='ON'))
        self.cfg.set('OPTIONS', 'SAVE_SQLITE', config.get('OPTIONS', 'SAVE_SQLITE', fallback='OFF'))
        self.cfg.add_section('PATH')  # PATH CONFIG
        self.cfg.set('PATH', 'DIR', config.get('PATH', 'DIR', fallback='C:\\tmp\\'))
        self.cfg.set('PATH', 'RES_FILENAME', config.get('PATH', 'RES_FILENAME', fallback='fssp.csv'))
        self.cfg.add_section('POSTGRES')  # PG_SQL CONFIG
        self.cfg.set('POSTGRES', 'HOST', config.get('POSTGRES', 'HOST', fallback='localhost'))
        self.cfg.set('POSTGRES', 'DBNAME', config.get('POSTGRES', 'DBNAME', fallback='skuns'))
        self.cfg.set('POSTGRES', 'USER', config.get('POSTGRES', 'USER', fallback='postgres'))
        self.cfg.set('POSTGRES', 'PWD', config.get('POSTGRES', 'PWD', fallback='111'))
        self.cfg.add_section('FSSP.RU')  # FSSP CONFIG
        self.cfg.set('FSSP.RU', 'PAUSE', config.get('FSSP.RU', 'PAUSE', fallback='15'))
        self.cfg.set('FSSP.RU', 'TOKEN', config.get('FSSP.RU', 'TOKEN', fallback='k51UxJdRmtyZ'))
        self.cfg.set('FSSP.RU', 'URL', config.get('FSSP.RU', 'URL', fallback='https://api-ip.fssprus.ru/api/v1.0/'))
        self.cfg.add_section('LOGS')  # LOG CONFIG
        self.cfg.set('LOGS', 'SAVE', config.get('LOGS', 'SAVE', fallback='ON'))
        self.cfg.set('LOGS', 'LVL', config.get('LOGS', 'LVL', fallback='3'))
        self.log_file = 'Logs\\fssp_' + time.strftime("%d.%m.%y", time.localtime()) + '.log'
        if not configparser.ConfigParser().read('config.ini'):
            self.__to_log('Creating config file {} with default settings', 3, 'config.ini', c1=Color.inf)
        self.save_cfg()

    def save_cfg(self):
        with open('config.ini', 'w') as cfg_file:
            self.cfg.write(cfg_file)

    # Записать сообщение в лог файл
    def __to_log(self, msg: str, deep_lvl: int = 3, *args, **kwargs):
        """ Log handler. Use it to log in screen, application and log file.
            MSG: can be String or String with {} to input *args inside using msg.format
            kwargs: use to set color for text inside {} in application window (log_frame) if unset = Color.inf
            deep_lvl: it's MSG warning lvl. Possible: 1-Crit, 2-Fail, 3-All
        """
        next_index = self.log_f.index('fin')
        next_row_n = next_index.split('.')[0]
        if msg is False:
            msg = 'Try to put empty message in log'
            deep_lvl = 1
        if deep_lvl == 1:
            echo = '\x1b[31m[CRIT]\x1b[0m ' + msg
            msg = '[CRIT] ' + msg
            lvl_color = Color.crit
        elif deep_lvl == 2:
            echo = '\x1b[33m[FAIL]\x1b[0m ' + msg
            msg = '[FAIL] ' + msg
            lvl_color = Color.fail
        else:
            echo = '\x1b[94m[INFO]\x1b[0m ' + msg
            msg = '[INFO] ' + msg
            lvl_color = Color.info
        msg = time.strftime("%d.%m.%y %H:%M:%S", time.localtime()) + ' ' + msg
        print(echo.format(*['\33[93m' + str(var) + '\33[0m' for var in args]))
        msg_copy = msg
        msg = msg.format(*args)
        self.log_f.insert(next_index, "{}\n".format(msg))
        self.log_f.see(tk.END)
        self.log_f.tag_add(next_index + 'time', next_index, next_row_n + '.17')
        self.log_f.tag_config(next_index + 'time', foreground='#AA5')
        self.log_f.tag_add(next_index + 'err_lvl', next_row_n + '.18', next_row_n + '.24')
        self.log_f.tag_config(next_index + 'err_lvl', foreground=lvl_color)
        if '{}' in msg_copy:
            colors = [str(c) for c in kwargs.values()] if kwargs else []
            a_lens = [len(str(string)) for string in args]
            positions = [pos for pos, char in enumerate(msg_copy) if char == '{']
            args_lens = 0
            for i in range(len(positions)):
                start = positions[i] + args_lens
                end = next_row_n + '.' + str(start + a_lens[i])
                start = next_row_n + '.' + str(start)
                self.log_f.tag_add(start, start, end)
                self.log_f.tag_config(start, foreground=colors[i] if i < len(colors) else Color.inf)
                args_lens += a_lens[i] - 2  # 2 символа это {}
        if 'LOGS' in self.cfg.sections() and self.cfg.get('LOGS', 'SAVE') == 'ON':
            if int(self.cfg.get('LOGS', 'LVL')) >= deep_lvl:
                try:
                    with open(self.log_file, "a") as filo:
                        filo.write(msg + '\n')
                except Exception as err:
                    print(f'Log file error. {err}')

    @staticmethod
    def bind_hover(widget):
        enter_color = widget['highlightbackground']
        leave_color = widget['background']
        widget.bind('<Enter>', lambda event, bg=enter_color: widget.config(background=bg))
        widget.bind('<Leave>', lambda event, bg=leave_color: widget.config(background=bg))


class MainF(tk.Frame):
    # Фрейм главной страницы
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # self.config(bd=2, relief='groove')

        self.tree = ttk.Treeview(self, height=15, show='headings', padding=0, selectmode='browse',
                                 column=(
                                 'F', 'I', 'O', 'dr', 'dt', 'adr', 'court', 'rst', 'csum', 'comm', 'jail', 'sum'),
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

    def view_records(self, arr):
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values=row) for row in arr]


class SettingsF(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.__app = controller
        font = ('Verdana', 12)  # Times/Verdana/Lucida/Tempus Sans ITC/Console/Courier/Helvetica
        font_big = ('Tempus Sans ITC', 16, 'bold')
        self.config(bd=2, relief='groove')
        # StringVar Setting
        self.__o_m_save = tk.StringVar()
        self.__o_m_renew = tk.StringVar()
        self.__o_m_sqlite = tk.StringVar()
        self.__o_p_dir = tk.StringVar()
        self.__o_p_name = tk.StringVar()
        self.__o_f_pause = tk.StringVar()
        self.__o_f_token = tk.StringVar()
        self.__o_f_url = tk.StringVar()
        self.__o_l_save = tk.StringVar()
        self.__o_l_lvl = tk.StringVar()
        self.__o_pg_host = tk.StringVar()
        self.__o_pg_name = tk.StringVar()
        self.__o_pg_user = tk.StringVar()
        self.__o_pg_pass = tk.StringVar()

        self.__settings_get()
        self.__trace()  # No buttons in trace - only inputs. Buttons have command function.

        # ======== MAIN OPTIONS =========================================
        opt_main = tk.Frame(self, bd=2, relief='groove')
        opt_main.grid(row=0, column=0, padx=5, ipadx=0, pady=5, ipady=5, sticky='WEN')
        tk.Label(opt_main, text='Main Settings', font=font_big).grid(row=0, column=0, columnspan=2)
        tk.Label(opt_main, text='Save results', anchor='w', width=15).grid(row=1, column=0, sticky='EW', padx=5)
        tk.Button(opt_main, textvariable=self.__o_m_save, width=3,
                  command=lambda: self.__change(self.__o_m_save, 'b')).grid(row=1, column=1)
        tk.Label(opt_main, text='Renew file', anchor='w').grid(row=2, column=0, sticky='EW', padx=5)
        tk.Button(opt_main, textvariable=self.__o_m_renew, width=3,
                  command=lambda: self.__change(self.__o_m_renew, 'b')).grid(row=2, column=1)
        tk.Label(opt_main, text='Save to SQLite', anchor='w').grid(row=3, column=0, sticky='EW', padx=5)
        tk.Button(opt_main, textvariable=self.__o_m_sqlite, width=3,
                  command=lambda: self.__change(self.__o_m_sqlite, 'b')).grid(row=3, column=1)
        # ======== LOGS OPTIONS =========================================
        opt_logs = tk.Frame(self, bd=2, relief='groove')
        opt_logs.grid(row=2, column=0, padx=5, ipadx=5, pady=5, ipady=5, sticky='WENS')
        tk.Label(opt_logs, text='Logs Settings', font=font_big).grid(row=0, column=0, columnspan=2)
        tk.Label(opt_logs, text='Save logs', anchor='w', width=15).grid(row=1, column=0, sticky='EW', padx=5)
        tk.Button(opt_logs, textvariable=self.__o_l_save, width=3,
                  command=lambda: self.__change(self.__o_l_save, 'b')).grid(row=1, column=1)
        tk.Label(opt_logs, text='Log level', anchor='w').grid(row=2, column=0, sticky='EW', padx=5)
        tk.Button(opt_logs, textvariable=self.__o_l_lvl, width=3,
                  command=lambda: self.__change(self.__o_l_lvl, 'lvl')).grid(row=2, column=1)
        # ======== FSSP OPTIONS =========================================
        opt_fssp = tk.Frame(self, bd=2, relief='groove', padx=5)
        opt_fssp.grid(row=0, column=1, padx=0, ipadx=0, pady=5, ipady=5, columnspan=2, sticky='WEN')
        tk.Label(opt_fssp, text='FSSP Settings', font=font_big).grid(row=0, column=0, columnspan=3)
        tk.Label(opt_fssp, text='API URL', anchor='w').grid(row=1, column=0, sticky='EW')
        tk.Entry(opt_fssp, textvariable=self.__o_f_url, width=30).grid(row=1, column=1, columnspan=2)
        tk.Label(opt_fssp, text='TOKEN', anchor='w').grid(row=2, column=0, sticky='EW')
        tk.Entry(opt_fssp, textvariable=self.__o_f_token).grid(row=2, column=1, sticky='EW')
        tk.Button(opt_fssp, text='CHECK', width=6).grid(row=2, column=2, rowspan=2, sticky='NS')
        tk.Label(opt_fssp, text='PAUSE', anchor='w').grid(row=3, column=0, sticky='EW')
        tk.Entry(opt_fssp, textvariable=self.__o_f_pause).grid(row=3, column=1, sticky='EW')
        # ======== PATH OPTIONS =====================================
        opt_path = tk.Frame(self, bd=2, relief='groove', padx=5)
        opt_path.grid(row=2, column=1, padx=5, ipadx=0, pady=5, ipady=5, sticky='WEN')
        tk.Label(opt_path, text='Path Settings', font=font_big).grid(row=0, column=0, columnspan=2)
        tk.Label(opt_path, text='Directory', anchor='w').grid(row=1, column=0, sticky='EW')
        tk.Entry(opt_path, textvariable=self.__o_p_dir).grid(row=1, column=1)
        tk.Label(opt_path, text='result file', anchor='w').grid(row=2, column=0, sticky='EW')
        tk.Entry(opt_path, textvariable=self.__o_p_name).grid(row=2, column=1)
        # ======== Postgres OPTIONS =====================================
        opt_pg = tk.Frame(self, bd=2, relief='groove', padx=5)
        opt_pg.grid(row=0, column=3, padx=5, ipadx=0, pady=5, ipady=5, sticky='WEN')
        tk.Label(opt_pg, text='Postgres Settings', font=font_big).grid(row=0, column=0, columnspan=2)
        tk.Label(opt_pg, text='Hostname', anchor='w').grid(row=1, column=0, sticky='EW')
        tk.Entry(opt_pg, textvariable=self.__o_pg_host, width=12).grid(row=1, column=1)
        tk.Label(opt_pg, text='DB name', anchor='w').grid(row=2, column=0, sticky='EW')
        tk.Entry(opt_pg, textvariable=self.__o_pg_name, width=12).grid(row=2, column=1)
        tk.Label(opt_pg, text='DB user', anchor='w').grid(row=3, column=0, sticky='EW')
        tk.Entry(opt_pg, textvariable=self.__o_pg_user, width=12).grid(row=3, column=1)
        tk.Label(opt_pg, text='Password', anchor='w').grid(row=4, column=0, sticky='EW')
        tk.Entry(opt_pg, textvariable=self.__o_pg_pass, width=12, show='*').grid(row=4, column=1)
        # ======== RESTORE DEFAULTS BUTTON =====================================
        btn_save = tk.Button(self, bd=2, padx=5, font=font_big, text='DEFAULTS', command=self.__defaults)
        btn_save.grid(row=2, column=3, padx=5, ipadx=0, pady=5, ipady=5, rowspan=2, sticky='WEN')

    def __settings_get(self):
        self.__o_m_save.set(self.__app.cfg['OPTIONS']['SAVE_TO_FILE'])
        self.__o_m_renew.set(self.__app.cfg['OPTIONS']['FILE_RENEW'])
        self.__o_m_sqlite.set(self.__app.cfg['OPTIONS']['SAVE_SQLITE'])

        self.__o_p_dir.set(self.__app.cfg['PATH']['DIR'])
        self.__o_p_name.set(self.__app.cfg['PATH']['RES_FILENAME'])

        self.__o_f_token.set(self.__app.cfg['FSSP.RU']['TOKEN'])
        self.__o_f_url.set(self.__app.cfg['FSSP.RU']['URL'])
        self.__o_f_pause.set(self.__app.cfg['FSSP.RU']['PAUSE'])

        self.__o_l_save.set(self.__app.cfg['LOGS']['SAVE'])
        self.__o_l_lvl.set(self.__app.cfg['LOGS']['LVL'])

        self.__o_pg_host.set(self.__app.cfg['POSTGRES']['HOST'])
        self.__o_pg_name.set(self.__app.cfg['POSTGRES']['DBNAME'])
        self.__o_pg_user.set(self.__app.cfg['POSTGRES']['USER'])
        self.__o_pg_pass.set(self.__app.cfg['POSTGRES']['PWD'])

    def __settings_set(self, *args):
        self.__app.cfg.set('OPTIONS', 'SAVE_TO_FILE', self.__o_m_save.get())
        self.__app.cfg.set('OPTIONS', 'FILE_RENEW', self.__o_m_renew.get())
        self.__app.cfg.set('OPTIONS', 'SAVE_SQLITE', self.__o_m_sqlite.get())

        self.__app.cfg.set('PATH', 'DIR', self.__o_p_dir.get())
        self.__app.cfg.set('PATH', 'RES_FILENAME', self.__o_p_name.get())

        self.__app.cfg.set('FSSP.RU', 'URL', self.__o_f_url.get())
        self.__app.cfg.set('FSSP.RU', 'TOKEN', self.__o_f_token.get())
        self.__app.cfg.set('FSSP.RU', 'PAUSE', self.__o_f_pause.get() if len(self.__o_f_pause.get()) > 0 else '5')

        self.__app.cfg.set('LOGS', 'SAVE', self.__o_l_save.get())
        self.__app.cfg.set('LOGS', 'LVL', self.__o_l_lvl.get())

        self.__app.cfg.set('POSTGRES', 'HOST', self.__o_pg_host.get())
        self.__app.cfg.set('POSTGRES', 'DBNAME', self.__o_pg_name.get())
        self.__app.cfg.set('POSTGRES', 'USER', self.__o_pg_user.get())
        self.__app.cfg.set('POSTGRES', 'PWD', self.__o_pg_pass.get())

        self.__app.save_cfg()

    def __change(self, var, typo='b'):
        v = var.get()
        if typo == 'b':
            var.set('ON') if v == 'OFF' else var.set('OFF')
        elif typo == 'lvl':
            var.set('1') if v == '3' else var.set('2') if v == '1' else var.set('3')
        self.__settings_set()

    def __defaults(self):
        self.__trace(False)
        self.__app.cfg.remove_section('OPTIONS')
        self.__app.cfg.remove_section('PATH')
        self.__app.cfg.remove_section('POSTGRES')
        self.__app.cfg.remove_section('FSSP.RU')
        self.__app.cfg.remove_section('LOGS')
        self.__app.save_cfg()
        self.__app.get_config()
        self.__settings_get()
        self.__trace()

    def __trace(self, on=True):
        """ Turn on/off tracking inputs change. If changed - save new value (real - all values) to config
            All StringVars can be put in tuple. But if I did it - no reason to remake, no memory for this tuple :)
        """
        if on:
            self.__o_p_dir.trace("w", self.__settings_set)
            self.__o_p_name.trace("w", self.__settings_set)
            self.__o_f_pause.trace("w", self.__settings_set)
            self.__o_f_token.trace("w", self.__settings_set)
            self.__o_f_url.trace("w", self.__settings_set)
            self.__o_pg_host.trace("w", self.__settings_set)
            self.__o_pg_name.trace("w", self.__settings_set)
            self.__o_pg_user.trace("w", self.__settings_set)
            self.__o_pg_pass.trace("w", self.__settings_set)
        else:
            self.__trace_clear(self.__o_p_dir)
            self.__trace_clear(self.__o_p_name)
            self.__trace_clear(self.__o_f_pause)
            self.__trace_clear(self.__o_f_token)
            self.__trace_clear(self.__o_f_url)
            self.__trace_clear(self.__o_pg_host)
            self.__trace_clear(self.__o_pg_name)
            self.__trace_clear(self.__o_pg_user)
            self.__trace_clear(self.__o_pg_pass)

    @staticmethod
    def __trace_clear(str_var):
        for t in str_var.trace_vinfo():
            str_var.trace_vdelete(*t)


if __name__ == '__main__':
    app = App()
    app.mainloop()
