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


class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        # App window Settings
        self.title("Проверяльщик ФССП")  # Название
        self.geometry('+500+300')  # Смещение окна
        self.resizable(False, False)  # Растягивается
        self.iconbitmap(self, default='.\\img\\fssp\\ico.ico')  # Иконка приложения
        # Отображаемые модули\виджиты на главном фрейме
        self.__menu_bar()
        self.__tool_bar()
        # Табло для отображения логов
        self.__log_f = tk.Text(self, height=12, bg='#001', fg='#AAA', selectbackground='#118', padx=10)
        self.__log_f.pack(side='bottom', fill='both', padx=2, pady=2)
        self.__log_f.mark_set('fin', '1.0')  # Делаем метку для прокрутки\вставки
        # Провереям конфиг и пути - (пути наверное не нужно)
        self._chk_paths()
        # Создаем верхний фрейм, куда будем пихать другие страницы\фреймы
        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True, padx=2)
        # Загружаем фреймы
        self.__frames = {}
        for F in (MainF, SettingsF):  # Список всех фреймов
            frame = F(container, self)
            self.__frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')
        # При запуске инициализируем конфиг и показываем заглавную страницу
        self.__threads = []
        self.__trace_connections = tk.IntVar(value=3)   # Update when thread finish. Can't use sqlite form thread.
        self.__trace_connections.trace("w", self.__use_filter)
        self.__init_connections()
        self.__show_frame(MainF)
        self.__filter = {'uniq': False}
        self.__use_filter()

    # GUI Element
    def __menu_bar(self):
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

    # GUI Element
    def __tool_bar(self):
        font = ('helvetica', 27)  # "Arial 24"
        # ToolBar Frame
        toolbar = tk.Frame(self, bg=Color.bg_end, bd=1, relief='solid')
        toolbar.pack(side='top', fill='both', padx=2)
        # ICONS
        self.settings_ico = tk.PhotoImage(file='.\\img\\fssp\\settings.png')
        self.home_ico = tk.PhotoImage(file='.\\img\\fssp\\home.png')
        self.btn_r_ico = tk.PhotoImage(file='.\\img\\fssp\\btn_r.png')
        self.btn_y_ico = tk.PhotoImage(file='.\\img\\fssp\\btn_y.png')
        self.btn_g_ico = tk.PhotoImage(file='.\\img\\fssp\\btn_g.png')
        self.one_ico = tk.PhotoImage(file='.\\img\\fssp\\one.png')
        self.all_ico = tk.PhotoImage(file='.\\img\\fssp\\all.png')
        self.search_ico = tk.PhotoImage(file='.\\img\\fssp\\search.png')
        self.save_ico = tk.PhotoImage(file='.\\img\\fssp\\save.png')
        self.mail_ico = tk.PhotoImage(file='.\\img\\fssp\\mail.png')
        ''' ToolBar elements '''
        self.btn_s = tk.Button(toolbar, command=lambda: self.__tool_bar_btn('settings'), image=self.settings_ico,
                               bg=Color.bg, bd=0, highlightbackground=Color.bg_hl)
        self.btn_s.pack(side='left', fill='both', ipadx=3)
        self.bind_hover(self.btn_s)

        self.__busy = tk.Label(toolbar, image=self.btn_g_ico, bg=Color.bg)
        self.__busy.pack(side='left', fill='both', ipadx=2, padx=1)

        self.btn_uniq = tk.Button(toolbar, command=lambda: self.__tool_bar_btn('one'), image=self.all_ico, bg=Color.bg,
                                  bd=0, highlightbackground=Color.bg_hl)
        self.btn_uniq.pack(side='left', fill='both', ipadx=5)
        self.bind_hover(self.btn_uniq)

        tk.Label(toolbar, font=font, text='С', bg=Color.bg, fg=Color.fg).pack(side='left', fill='both', ipadx=2)
        self.start_date = DateEntry(toolbar, font=font, bd=0, bg=Color.bg, fg='#000', highlightbackground='#beb')
        self.start_date.pack(side='left', fill='both')
        CalPopup(self.start_date, bd=0, bg=Color.bg, fg='#000', highlightbackground=Color.bg_hl)
        self.start_date.date = time.strftime("%Y-%m-%d", time.localtime(time.time()-86400*30))

        tk.Label(toolbar, font=font, text='По', bg=Color.bg, fg=Color.fg).pack(side='left', fill='both', ipadx=2)
        self.end_date = DateEntry(toolbar, font=font, bd=0, bg=Color.bg, fg='#000', highlightbackground='#beb')
        self.end_date.pack(side='left', fill='both')
        CalPopup(self.end_date, bd=0, bg=Color.bg, fg='#000', highlightbackground=Color.bg_hl)
        self.end_date.date = time.strftime("%Y-%m-%d", time.localtime(time.time()+86400))

        self.btn_search = tk.Button(toolbar, command=lambda: self.__use_filter(), image=self.search_ico, bg=Color.bg,
                                    bd=0, highlightbackground=Color.bg_hl)
        self.btn_search.pack(side='left', fill='both', ipadx=5, padx=1)
        self.bind_hover(self.btn_search)

        self.btn_save = tk.Button(toolbar, command=self.__save_data, image=self.save_ico, bg=Color.bg, state='disabled',
                                  bd=0, highlightbackground=Color.bg_hl)
        self.btn_save.pack(side='left', fill='both', ipadx=4)
        self.bind_hover(self.btn_save)

        self.btn_mail = tk.Button(toolbar, command=self.__save_data, image=self.mail_ico, bg=Color.bg, state='disabled',
                                  bd=0, highlightbackground=Color.bg_hl)
        self.btn_mail.pack(side='left', fill='both', ipadx=4, padx=1)
        self.bind_hover(self.btn_mail)

        author = tk.Label(toolbar, font=('Console', 9, 'bold'), text='Version: 0.82 \nAuthor: meok', bg='#6CF')
        author.pack(side='left', fill='both', expand=True)

    # GUI Element behaviour
    def __tool_bar_btn(self, where=None):
        if where == 'settings':
            self.btn_s.config(image=self.home_ico)
            self.btn_s.config(command=lambda: self.__tool_bar_btn('home'))
            self.__show_frame(SettingsF)
        elif where == 'home':
            self.btn_s.config(image=self.settings_ico)
            self.btn_s.config(command=lambda: self.__tool_bar_btn('settings'))
            self.__init_connections()
            self.__show_frame(MainF)
        elif where == 'one':
            self.btn_uniq.config(image=self.one_ico)
            self.btn_uniq.config(command=lambda: self.__tool_bar_btn('all'))
            self.__filter['uniq'] = True
            self.__use_filter()
        elif where == 'all':
            self.btn_uniq.config(image=self.all_ico)
            self.btn_uniq.config(command=lambda: self.__tool_bar_btn('one'))
            self.__filter['uniq'] = False
            self.__use_filter()

    def __use_filter(self, *args):
        uniq = self.__filter['uniq']    # Add here if new values
        self.__filter['start'] = self.start_date.date
        self.__filter['end'] = self.end_date.date
        self.__frames[MainF].filter = self.__filter   # After call - filter lose value (cos using pop)
        self.__filter = {'uniq': uniq, 'start': self.start_date.date, 'end': self.end_date.date}

    def _chk_paths(self, path_type='all'):
        cur_dir = os.getcwd() + '\\'
        self._get_config()

        def logs(obj):
            if obj.cfg['LOGS']['SAVE'] == 'ON':    # Если логирование включено
                if os.path.isdir('Logs'):          # Проверка папки с логами
                    obj._to_log('Log folder {} exist - {}', 3, cur_dir + 'Logs', 'OK', c1=Color.inf, c2=Color.ok)
                else:
                    try:
                        os.makedirs('Logs')
                        obj._to_log('Log folder {} created - {}', 3, cur_dir + 'Logs', 'OK', c1=Color.inf, c2=Color.ok)
                    except Exception as e:
                        obj._to_log('Log folder {} creating - {} Err:{}', 1,
                                     cur_dir + 'Logs', 'fail', e, c1=Color.inf, c2=Color.err, c3=Color.info)
                        obj._to_log('Set {} = {}', 1, 'LOG_TO_FILE', 'False', c1=Color.inf, c2=Color.fail)
                        return False
            if os.path.isfile(obj.log_file):   # Проверка файла логов
                print('Log file\33[93m', cur_dir + obj.log_file, '\33[0mexist - \33[32mOK\33[0m')
                return True
            else:
                try:
                    filo = open(obj.log_file, "w")
                    filo.write(time.strftime("%d.%m.%Y %H:%M:%S", time.localtime()) +
                               ' [INFO] Created file log ' + cur_dir + obj.log_file + '\n')
                    filo.close()
                    print('Log file\33[93m', cur_dir + obj.log_file, '\33[0mcreated - \33[32mOK\33[0m')
                except Exception as e:
                    print('Log file\33[93m', cur_dir + obj.log_file, '\33[0mcreating - \33[91mfail.', e, '\33[0m')
                    print('\33[91mSet LOG_TO_FILE = False\33[0m')
                    return False
                else:
                    return True

        def result_dir(obj):    # Проверием папки для файла с результатами
            if self.cfg['OPTIONS']['SAVE_TO_FILE'] == 'ON':
                if os.path.isdir(obj.cfg['PATH']['DIR']):  # Проверка основной папки
                    print('Main folder\33[93m', obj.cfg['PATH']['DIR'], '\33[0mexist - \33[32mOK\33[0m')
                else:
                    try:
                        os.makedirs(obj.cfg['PATH']['DIR'])
                        print('Main folder\33[93m', obj.cfg['PATH']['DIR'], '\33[0m created - \33[32mOK\33[0m')
                    except Exception as e:
                        print('Main folder\33[93m', obj.cfg['PATH']['DIR'], '\33[0m creating - \33[91mfail.', e,
                              '\33[0m')
                        print('\33[91mSet SAVE_RESULT = False\33[0m')
                        obj.cfg.set('OPTIONS', 'SAVE_TO_FILE', 'OFF')
                        return False
                    else:
                        return True
            else:
                print('No save file will be used.\33[0m')
                return False

        def result(obj):    # Создаем файл с результатами
            if result_dir(obj) and obj.cfg['OPTIONS']['SAVE_TO_FILE'] == 'ON':
                res_file_path = obj.cfg['PATH']['DIR'] + obj.cfg['PATH']['RES_FILENAME']
                if not os.path.isfile(res_file_path) or obj.cfg['OPTIONS']['FILE_RENEW'] == 'ON':
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
                        obj.cfg.set('OPTIONS', 'SAVE_TO_FILE', 'OFF')
                        return False
                    else:
                        return True
                else:
                    print('Result file\33[93m', res_file_path, '\33[0mexist - \33[32mOK\33[0m')
            return True

        if path_type == 'all':
            self._to_log("Application directory: {}", 3, cur_dir)
            # Проверием структуру файлов\папок
            if self.cfg['OPTIONS']['SAVE_TO_FILE'] == 'ON' or self.cfg['LOGS']['SAVE'] == 'ON':
                self._to_log('Checking folders structure...')
                return True if (logs(self) and result_dir(self)) else False
            else:
                self._to_log('No files will be used {}.', 3, 'Echo mode', c=Color.inf)
                return True
        elif path_type == 'logs':
            return True if logs(self) else False
        elif path_type == 'r_dir':
            return True if result_dir(self) else False
        elif path_type == 'result':
            return True if result(self) else False
        return False

    def __init_connections(self):
        """ This function run 'connections' in other thread cos getting FSSP data sometimes needs a lot of time. """
        for x in self.__threads:
            if x.is_alive():
                self._to_log('Already connecting. Wait while finish.', 3)  # Thread busy
                return False
        self._to_log('Trying connections...', 3)  # Thread free
        thr = threading.Thread(target=self.__connections)  # Поскольку в процессе есть запрос к бд thread
        self.__threads.append(thr)
        thr.start()
        return True

    def __connections(self):
        """ Update data function. First get last update time. Then we request PG_DB for new visits.
            Then get FSSP data. When busy - turn red light on GUI. """
        self._get_config()
        self.__busy.config(image=self.btn_y_ico)  # Turn light - BLUE
        db = DbLocal('fssp', self._to_log)
        db_pg = DataBase({'host': self.cfg['POSTGRES']['HOST'], 'dbname': self.cfg['POSTGRES']['DBNAME'],
                          'user': self.cfg['POSTGRES']['USER'], 'pwd': self.cfg['POSTGRES']['PWD']}, self._to_log)
        fssp = FSSP(self.cfg['FSSP.RU']['TOKEN'], self.cfg['FSSP.RU']['PAUSE'], self.cfg['FSSP.RU']['URL'],
                    self._to_log)
        db.visits = db_pg.select_sql(db.visits[4])  # Select visits and then insert in local DB
        db_pg.close()
        if db.data:                 # New users from visits
            self.__busy.config(image=self.btn_r_ico)  # Turn light - RED
            fssp.arr = db.data      # Request FSSP with new users.
            for x in fssp.arr:      # Insert new sums for users\visits
                db.data = ('sum', *x[1:5], time.strftime("%Y-%m-%d", time.localtime()), x[5])
        self.__busy.config(image=self.btn_g_ico)  # Turn light - GREEN
        self.__trace_connections.set(1)

    def __save_data(self):
        print('SAVING ))')
        pass

    def __show_frame(self, context):  # Вывод на передний план фрейма
        self.__frames[context].tkraise()

    def _get_config(self):   # Used in SettingsF class
        self.cfg = configparser.ConfigParser()
        config = configparser.ConfigParser()
        if config.read('config.ini'):
            self._to_log('Reading config file {} - {}', 3, 'config.ini', 'OK', c1=Color.inf, c2=Color.ok)
        else:
            self._to_log('Reading config file {} - {}', 1, 'config.ini', 'Fail', c1=Color.inf, c2=Color.fail)
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
            self._to_log('Creating config file {} with default settings', 3, 'config.ini', c1=Color.inf)
        self._save_cfg()

    def _save_cfg(self):
        with open('config.ini', 'w') as cfg_file:
            self.cfg.write(cfg_file)

    def _to_log(self, msg: str, deep_lvl: int = 3, *args, **kwargs):
        """ Log handler. Use it to log in screen, application and log file.
            MSG: can be String or String with {} to input *args inside using msg.format
            kwargs: use to set color for text inside {} in application window (log_frame) if unset = Color.inf
            deep_lvl: it's MSG warning lvl. Possible: 1-Crit, 2-Fail, 3-All
        """
        next_index = self.__log_f.index('fin')
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
        msg = time.strftime("%d.%m.%Y %H:%M:%S", time.localtime()) + ' ' + msg
        print(echo.format(*['\33[93m' + str(var) + '\33[0m' for var in args]))
        msg_copy = msg
        msg = msg.format(*args)
        self.__log_f.insert(next_index, "{}\n".format(msg))
        self.__log_f.see(tk.END)
        self.__log_f.tag_add(next_index + 'time', next_index, next_row_n + '.19')
        self.__log_f.tag_config(next_index + 'time', foreground='#AA5')
        self.__log_f.tag_add(next_index + 'err_lvl', next_row_n + '.20', next_row_n + '.26')
        self.__log_f.tag_config(next_index + 'err_lvl', foreground=lvl_color)
        if '{}' in msg_copy:
            colors = [str(c) for c in kwargs.values()] if kwargs else []
            a_lens = [len(str(string)) for string in args]
            positions = [pos for pos, char in enumerate(msg_copy) if char == '{']
            args_lens = 0
            for i in range(len(positions)):
                start = positions[i] + args_lens
                end = next_row_n + '.' + str(start + a_lens[i])
                start = next_row_n + '.' + str(start)
                self.__log_f.tag_add(start, start, end)
                self.__log_f.tag_config(start, foreground=colors[i] if i < len(colors) else Color.inf)
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

        self.__tree = ttk.Treeview(self, height=15, show='headings', padding=0, selectmode='browse',
                                   column=(
                                 'F', 'I', 'O', 'dr', 'dt', 'adr', 'court', 'rst', 'csum', 'comm', 'jail', 'sum'),
                                   displaycolumns=('dt', 'adr', 'court', 'rst', 'csum', 'comm', 'jail', 'sum'))
        # Таблица для вывода результатов
        self.__tree.column('dt', width=110, anchor=tk.CENTER)
        self.__tree.column('adr', width=250, anchor=tk.W)
        self.__tree.column('court', width=55, anchor=tk.CENTER)
        self.__tree.column('rst', width=50, anchor=tk.CENTER)
        self.__tree.column('csum', width=130, anchor=tk.W)
        self.__tree.column('comm', width=250, anchor=tk.W, stretch=True)
        self.__tree.column('jail', width=80, anchor=tk.CENTER)
        self.__tree.column('sum', width=110, anchor=tk.CENTER)

        self.__tree.heading('dt', text='Время')
        self.__tree.heading('adr', text='Адрес')
        self.__tree.heading('court', text='Участок')
        self.__tree.heading('rst', text='Реестр')
        self.__tree.heading('csum', text='Контрольная сумма')
        self.__tree.heading('comm', text='Комментарий')
        self.__tree.heading('jail', text='Задержаний')
        self.__tree.heading('sum', text='Сумма взысканий')

        self.__tree.pack(side='top', fill='both')
        self.__tree.bind('<<TreeviewSelect>>', self.__select_record)

        self.__db = DbLocal('fssp', controller._to_log)
        #self.filter = {'uniq': False}

    def view_records(self):
        [self.__tree.delete(i) for i in self.__tree.get_children()]
        [self.__tree.insert('', 'end', values=row) for row in self.__db.table]

    def __select_record(self, event):
        PopUp(self.__tree, self.__db)
        pass

    @property
    def filter(self):
        return True

    @filter.setter
    def filter(self, conditions):
        self.__db.table = conditions
        self.view_records()


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

        self.__app._save_cfg()

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
        self.__app._save_cfg()
        self.__app._get_config()
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


class PopUp(tk.Toplevel):
    def __init__(self, tree, db, *args, **kwargs):
        super().__init__()
        self.row_id = tree.selection()[0]  # row ID
        self.__tree = tree
        self.__db = db
        x = tree.winfo_rootx() + 240
        y = tree.winfo_rooty() + 25 + tree.index(self.row_id) * 20   # 25 - headers, 20 - row height проверить на > 15
        self.geometry('+{}+{}'.format(x, y))    # Смещение окна
        self.overrideredirect(1)                # Убрать TitleBar
        self.title('Добавить доходы\расходы')
        self.bind('<FocusOut>', lambda event: self.destroy())   # When PopUp lose focus
        self.resizable(False, False)
        self.focus_force()
        self.config(bg=Color.bg_end, highlightcolor=Color.bg_end, highlightthickness=1)

        self.fssp_ico = tk.PhotoImage(file='.\\img\\fssp\\fssp.png')
        self.pristav_ico = tk.PhotoImage(file='.\\img\\fssp\\pristav.png')
        self.db_y_ico = tk.PhotoImage(file='.\\img\\fssp\\db_y.png')
        self.db_n_ico = tk.PhotoImage(file='.\\img\\fssp\\db_n.png')
        self.jail_y_ico = tk.PhotoImage(file='.\\img\\fssp\\jail_y.png')
        self.jail_n_ico = tk.PhotoImage(file='.\\img\\fssp\\jail_n.png')
        self.ok_ico = tk.PhotoImage(file='.\\img\\fssp\\ok.png')
        self.cancel_ico = tk.PhotoImage(file='.\\img\\fssp\\cancel.png')

        # Захват окна
        #self.grab_set()
        #self.focus_get()

        self.row_id = tree.selection()[0]  # row ID
        self.row = tree.item(self.row_id)['values']

        font_s = ('helvetica', 8)
        font = ('helvetica', 10)
        font_b = ('helvetica', 16)

        find_idx = self.row[9].upper().find('ПРИСТАВУ')
        if find_idx > -1:
            to = ('Приставу', self.pristav_ico)
            txt_idx = find_idx + 9
        else:
            find_idx = self.row[9].upper().find('СООБЩИЛИ В ФССП')
            if find_idx > -1:
                to = ('ФССП', self.fssp_ico)
                txt_idx = find_idx + 16
            else:
                to = ('Приставу', self.pristav_ico) if int(self.row[4][-1:]) % 2 == 0 else ('ФССП', self.fssp_ico)
                txt_idx = 0

        find_idx = self.row[9].upper().find('БАЗЫ'), self.row[9].upper().find('БАЗЕ')
        find_idx = find_idx[0] if find_idx[0] > find_idx[1] else find_idx[1]
        if find_idx > -1:
            in_bd = ('Снят с базы', self.db_n_ico)
            txt_idx = find_idx + 5 if find_idx + 5 > txt_idx else txt_idx
        else:
            in_bd = ('Есть в базе', self.db_y_ico)
        text = self.row[9][txt_idx:].lstrip() if len(self.row[9]) > txt_idx and self.row[9] != 'None' else ''

        in_jail = ('Свободен', self.jail_n_ico) if self.row[10] in ('None', '') else ('Доставлен', self.jail_y_ico)

        fio = tk.Label(self, font=font_b, text='{} {} {}'.format(*self.row[0:3]), bg=Color.bg)
        fio.pack(side='top', fill='both', ipadx=5)

        c_sum_frame = tk.Frame(self, bg=Color.bg_end)
        c_sum_frame.pack(side='top', fill='both', ipadx=5, pady=1)
        tk.Label(c_sum_frame, font=font, text='Контрольная сумма:', bg=Color.bg).pack(side='left', fill='both', ipadx=5)
        tk.Label(c_sum_frame, font=font, text=self.row[8], bg=Color.bg, anchor='w').pack(side='left', fill='both', expand=True)

        btn_frame = tk.Frame(self, bg='#333')
        btn_frame.pack(side='top', fill='both', expand=True)

        btn_def = {'compound': 'top', 'highlightbackground': Color.bg_hl, 'bg': Color.bg2, 'bd': 0}
        tk.Label(btn_frame, font=font, text='Сообщили', bg=Color.bg, width=10).grid(row=0, column=0, sticky='NSEW')
        self.btn_to = tk.Button(btn_frame, text=to[0], image=to[1], command=lambda: self.__clicked('say_to'), **btn_def)
        self.btn_to.grid(row=1, column=0, sticky='NSEW')
        App.bind_hover(self.btn_to)
        tk.Label(btn_frame, font=font, text='В реестре', bg=Color.bg, width=10).grid(row=0, column=1, sticky='NSEW', padx=1)
        self.btn_db = tk.Button(btn_frame, text=in_bd[0], image=in_bd[1], command=lambda: self.__clicked('db'), **btn_def)
        self.btn_db.grid(row=1, column=1, sticky='NSEW', padx=1)
        App.bind_hover(self.btn_db)
        tk.Label(btn_frame, font=font, text='Задержан', bg=Color.bg, width=10).grid(row=0, column=2, sticky='NSEW')
        self.btn_jail = tk.Button(btn_frame, text=in_jail[0], image=in_jail[1], command=lambda: self.__clicked('jail'), **btn_def)
        self.btn_jail.grid(row=1, column=2, sticky='NSEW')
        App.bind_hover(self.btn_jail)

        tk.Label(btn_frame, font=font, text='Комментарий', bg=Color.bg, width=10).grid(row=0, column=3, sticky='NSEW', padx=1)
        self.text_f = tk.Text(btn_frame, font=font, width=20, height=3, bd=0)
        self.text_f.grid(row=1, column=3, sticky='NSEW', padx=1)
        self.text_f.insert('end', text)

        tk.Label(btn_frame, font=font, text='Сохранить изменения', bg=Color.bg, width=18).grid(row=0, column=4, sticky='NSEW', columnspan=2)
        ok = tk.Button(btn_frame, text='ОК', image=self.ok_ico, width=9, bd=0, highlightbackground=Color.bg_hl, bg=Color.bg2, command=self.__save)
        ok.grid(row=1, column=4, sticky='NSEW')
        App.bind_hover(ok)
        cancel = tk.Button(btn_frame, text='ОТМЕНА', image=self.cancel_ico, width=9, bd=0, highlightbackground=Color.bg_hl, bg=Color.bg2, command=self.destroy)
        cancel.grid(row=1, column=5, sticky='NSEW')
        App.bind_hover(cancel)

    def __clicked(self, btn_name):
        if btn_name == 'say_to':
            val = ('Приставу', self.pristav_ico) if self.btn_to['text'] == 'ФССП' else ('ФССП', self.fssp_ico)
            self.btn_to.config(text=val[0], image=val[1])
        elif btn_name == 'db':
            val = ('Есть в базе', self.db_y_ico) if self.btn_db['text'] == 'Снят с базы' else ('Снят с базы', self.db_n_ico)
            self.btn_db.config(text=val[0], image=val[1])
        elif btn_name == 'jail':
            val = ('Свободен', self.jail_n_ico) if self.btn_jail['text'] == 'Доставлен' else ('Доставлен', self.jail_y_ico)
            self.btn_jail.config(text=val[0], image=val[1])

    def __save(self):
        date = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(self.row[4], '%d.%m.%Y %H:%M:%S'))
        txt = 'Сообщили в ФССП. ' if self.btn_to['text'] == 'ФССП' else 'Сообщили приставу. '
        txt += 'Снят с базы. ' if self.btn_db['text'] == 'Снят с базы' else ''
        txt += self.text_f.get(1.0, 'end')[:-1]

        self.__tree.set(self.row_id, 'comm', txt)
        self.__db.data = ('comment', *self.row[0:4], date,  txt)

        if self.btn_jail['text'] == 'Доставлен':
            self.__tree.set(self.row_id, 'jail', 'ЗАДЕРЖАН')
            self.__db.data = ('jail', *self.row[0:4], date, 'ЗАДЕРЖАН')
        else:
            self.__tree.set(self.row_id, 'jail', 'None')
            self.__db.data = ('jail', *self.row[0:4], date, None)

        self.destroy()


if __name__ == '__main__':
    app = App()
    app.mainloop()
