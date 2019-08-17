import os
import re
import configparser
from calendar import TextCalendar
import xlsxwriter
import requests
import psycopg2
import sqlite3
from threading import Thread
import time
import tkinter as tk
from datetime import datetime
from tkinter import ttk
from tkinter.filedialog import asksaveasfile


class Color:
    time = '#AA5'
    inf = '#CC0'
    err = '#C33'
    ok = '#3B3'

    info = '#59F'
    fail = '#F93'
    crit = '#F00'

    hl = '#FF0'
    hl1 = '#F0F'
    hl2 = '#3F3'
    zero = '#FFF'

    bg = '#6DF'
    bg2 = '#9EF'
    bg_hl = '#39F'
    bg_end = '#33C'
    fg = '#000'


class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Проверяльщик ФССП")
        self.geometry('+500+300')
        self.resizable(False, False)
        self.iconbitmap(self, default='.\\img\\fssp\\ico.ico')
        self.__menu_bar()
        self.__tool_bar()
        self.__log_f = tk.Text(self, height=12, bg='#001', fg='#AAA', selectbackground='#118', padx=10)
        self.__log_f.pack(side='bottom', fill='both', padx=2, pady=2)
        self.__log_f.mark_set('fin', '1.0')
        self._chk_paths()
        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True, padx=2)
        self.__frames = {}
        for F in (MainF, SettingsF):
            frame = F(container, self)
            self.__frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')
        self.__threads = []
        self.__trace_connections = tk.IntVar(value=3)
        self.__trace_connections.trace("w", self.__use_filter)
        self.__init_connections()
        self.__show_frame(MainF)
        self.__filter = {'uniq': False}
        self.__use_filter()

    def __menu_bar(self):
        menu_bar = tk.Menu(self)
        file = tk.Menu(menu_bar, tearoff=0)
        file.add_command(label='New', command=lambda: self.__show_frame(MainF))
        file.add_command(label='Open')
        file.add_command(label='Save')
        file.add_command(label='Close')
        file.add_command(label='Options', command=lambda: self.__show_frame(SettingsF))
        file.add_separator()
        file.add_command(label='Exit', command=self.quit)
        edit = tk.Menu(menu_bar, tearoff=0)
        edit.add_command(label="Undo")
        edit.add_separator()
        edit.add_command(label="Cut")
        edit.add_command(label="Copy")
        edit.add_command(label="Paste")
        edit.add_command(label="Delete")
        edit.add_command(label="Select All")
        info = tk.Menu(menu_bar, tearoff=0)
        info.add_command(label="About")
        menu_bar.add_cascade(label='File', menu=file)
        menu_bar.add_cascade(label="Edit", menu=edit)
        menu_bar.add_cascade(label="Help", menu=info)
        self.config(menu=menu_bar)

    def __tool_bar(self):
        font = ('helvetica', 27)
        toolbar = tk.Frame(self, bg=Color.bg_end, bd=1, relief='solid')
        toolbar.pack(side='top', fill='both', padx=2)
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
        self.btn_s = tk.Button(toolbar, command=lambda: self.__tool_bar_btn('settings'), image=self.settings_ico, bg=Color.bg, bd=0, highlightbackground=Color.bg_hl)
        self.btn_s.pack(side='left', fill='both', ipadx=3)
        self.bind_hover(self.btn_s)
        self.__busy = tk.Label(toolbar, image=self.btn_g_ico, bg=Color.bg)
        self.__busy.pack(side='left', fill='both', ipadx=2, padx=1)
        self.btn_uniq = tk.Button(toolbar, command=lambda: self.__tool_bar_btn('one'), image=self.all_ico, bg=Color.bg, bd=0, highlightbackground=Color.bg_hl)
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
        self.btn_search = tk.Button(toolbar, command=lambda: self.__use_filter(), image=self.search_ico, bg=Color.bg, bd=0, highlightbackground=Color.bg_hl)
        self.btn_search.pack(side='left', fill='both', ipadx=5, padx=1)
        self.bind_hover(self.btn_search)
        self.btn_save = tk.Button(toolbar, command=self.__save_data, image=self.save_ico, bg=Color.bg, bd=0, highlightbackground=Color.bg_hl)
        self.btn_save.pack(side='left', fill='both', ipadx=4)
        self.bind_hover(self.btn_save)
        self.btn_mail = tk.Button(toolbar, command=self.__save_data, image=self.mail_ico, bg=Color.bg, state='disabled', bd=0, highlightbackground=Color.bg_hl)
        self.btn_mail.pack(side='left', fill='both', ipadx=4, padx=1)
        self.bind_hover(self.btn_mail)
        author = tk.Label(toolbar, font=('Console', 9, 'bold'), text='Version: 1.00 \nAuthor: meok', bg='#6CF')
        author.pack(side='left', fill='both', expand=True)

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
        uniq = self.__filter['uniq']
        self.__filter['start'] = self.start_date.date
        self.__filter['end'] = self.end_date.date
        self.__frames[MainF].filter = self.__filter
        self.__filter = {'uniq': uniq, 'start': self.start_date.date, 'end': self.end_date.date}

    def _chk_paths(self, path_type='all'):
        cur_dir = os.getcwd() + '\\'
        self._get_config()

        def logs(obj):
            if obj.cfg['LOGS']['SAVE'] == 'ON':
                if os.path.isdir('Logs'):
                    obj._to_log('Log folder {} exist - {}', 3, cur_dir + 'Logs', 'OK', c1=Color.inf, c2=Color.ok)
                else:
                    try:
                        os.makedirs('Logs')
                        obj._to_log('Log folder {} created - {}', 3, cur_dir + 'Logs', 'OK', c1=Color.inf, c2=Color.ok)
                    except Exception as e:
                        obj._to_log('Log folder {} creating - {} Err:{}', 1, cur_dir + 'Logs', 'fail', e, c1=Color.inf, c2=Color.err, c3=Color.info)
                        obj._to_log('Set {} = {}', 1, 'LOG_TO_FILE', 'False', c1=Color.inf, c2=Color.fail)
                        return False
            if os.path.isfile(obj.log_file):
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

        def result(obj):
            if self.cfg['OPTIONS']['SAVE_TO_FILE'] == 'ON':
                if os.path.isdir(obj.cfg['PATH']['DIR']):
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

        if path_type == 'all':
            self._to_log("Application directory: {}", 3, cur_dir)
            if self.cfg['LOGS']['SAVE'] == 'ON':
                self._to_log('Checking folders structure...')
                return logs(self)
            else:
                self._to_log('No files will be used {}.', 3, 'Echo mode', c=Color.inf)
                return True
        elif path_type == 'logs':
            return logs(self)
        elif path_type == 'result':
            return result(self)
        return False

    def __init_connections(self):
        for x in self.__threads:
            if x.is_alive():
                self._to_log('Already connecting. Wait while finish.', 3)
                return False
        self._to_log('Trying connections...', 3)
        thr = Thread(target=self.__connections)
        self.__threads.append(thr)
        thr.start()
        return True

    def __connections(self):
        self._get_config()
        self.__busy.config(image=self.btn_y_ico)
        db = DbLocal('fssp', self._to_log)
        db_pg = DataBase({'host': self.cfg['POSTGRES']['HOST'], 'dbname': self.cfg['POSTGRES']['DBNAME'],
                          'user': self.cfg['POSTGRES']['USER'], 'pwd': self.cfg['POSTGRES']['PWD']}, self._to_log)
        fssp = FSSP(self.cfg['FSSP.RU']['TOKEN'], self.cfg['FSSP.RU']['PAUSE'], self.cfg['FSSP.RU']['URL'],
                    self._to_log)
        db.visits = db_pg.select_sql(db.visits[4])
        db_pg.close()
        fssp_req_data = db.data
        if fssp_req_data:
            self.__busy.config(image=self.btn_r_ico)
            while len(fssp_req_data) != 0:
                if len(fssp_req_data) > 3:
                    req = [fssp_req_data.pop(), fssp_req_data.pop(), fssp_req_data.pop()]
                else:
                    req = [fssp_req_data.pop() for i in range(len(fssp_req_data))]
                fssp.arr = req
                for x in fssp.arr:
                    db.data = ('sum', *x[1:5], time.strftime("%Y-%m-%d", time.localtime()), x[5])
        self.__busy.config(image=self.btn_g_ico)
        self.__trace_connections.set(1)

    def __save_data(self):
        try:
            filename = asksaveasfile(title="Select file", filetypes=(("Excel files", "*.xlsx"), ("all files", "*.*")),
                                     defaultextension=("Excel files", "*.xlsx"), initialdir=self.cfg['PATH']['DIR'], initialfile=self.cfg['PATH']['RES_FILENAME'])
        except Exception as err:
            self._to_log('Unable to open file: {}', 1, err)
            return False
        else:
            filename.close()
            xls = Excel(str(filename.name), self._to_log)
            xls.data_from_db()

    def __show_frame(self, context):
        self.__frames[context].tkraise()

    def _get_config(self):
        self.cfg = configparser.ConfigParser()
        config = configparser.ConfigParser()
        if config.read('config.ini'):
            self._to_log('Reading config file {} - {}', 3, 'config.ini', 'OK', c1=Color.inf, c2=Color.ok)
        else:
            self._to_log('Reading config file {} - {}', 1, 'config.ini', 'Fail', c1=Color.inf, c2=Color.fail)
        self.cfg.add_section('OPTIONS')
        self.cfg.set('OPTIONS', 'SAVE_TO_FILE', config.get('OPTIONS', 'SAVE_TO_FILE', fallback='ON'))
        self.cfg.set('OPTIONS', 'FILE_RENEW', config.get('OPTIONS', 'FILE_RENEW', fallback='ON'))
        self.cfg.set('OPTIONS', 'SAVE_SQLITE', config.get('OPTIONS', 'SAVE_SQLITE', fallback='OFF'))
        self.cfg.add_section('PATH')
        self.cfg.set('PATH', 'DIR', config.get('PATH', 'DIR', fallback='C:\\tmp\\'))
        self.cfg.set('PATH', 'RES_FILENAME', config.get('PATH', 'RES_FILENAME', fallback='fssp.xlsx'))
        self.cfg.add_section('POSTGRES')
        self.cfg.set('POSTGRES', 'HOST', config.get('POSTGRES', 'HOST', fallback='localhost'))
        self.cfg.set('POSTGRES', 'DBNAME', config.get('POSTGRES', 'DBNAME', fallback='skuns'))
        self.cfg.set('POSTGRES', 'USER', config.get('POSTGRES', 'USER', fallback='postgres'))
        self.cfg.set('POSTGRES', 'PWD', config.get('POSTGRES', 'PWD', fallback='111'))
        self.cfg.add_section('FSSP.RU')
        self.cfg.set('FSSP.RU', 'PAUSE', config.get('FSSP.RU', 'PAUSE', fallback='15'))
        self.cfg.set('FSSP.RU', 'TOKEN', config.get('FSSP.RU', 'TOKEN', fallback='k51UxJdRmtyZ'))
        self.cfg.set('FSSP.RU', 'URL', config.get('FSSP.RU', 'URL', fallback='https://api-ip.fssprus.ru/api/v1.0/'))
        self.cfg.add_section('LOGS')
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
                args_lens += a_lens[i] - 2
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
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.__tree = ttk.Treeview(self, height=15, show='headings', padding=0, selectmode='browse',
                                   column=('F', 'I', 'O', 'dr', 'dt', 'adr', 'court', 'rst', 'csum', 'comm', 'jail', 'sum'),
                                   displaycolumns=('dt', 'adr', 'court', 'rst', 'csum', 'comm', 'jail', 'sum'))
        self.__tree.column('dt', width=110, anchor=tk.CENTER)
        self.__tree.column('adr', width=250, anchor=tk.W)
        self.__tree.column('court', width=55, anchor=tk.CENTER)
        self.__tree.column('rst', width=50, anchor=tk.CENTER)
        self.__tree.column('csum', width=130, anchor=tk.W)
        self.__tree.column('comm', width=250, anchor=tk.W, stretch=True)
        self.__tree.column('jail', width=80, anchor=tk.CENTER)
        self.__tree.column('sum', width=110, anchor=tk.E)
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

    def __view_records(self):
        [self.__tree.delete(i) for i in self.__tree.get_children()]
        [self.__tree.insert('', 'end', values=row) for row in self.__db.table]

    def __select_record(self, event):
        PopUp(self.__tree, self.__db)

    @property
    def filter(self):
        return True

    @filter.setter
    def filter(self, conditions):
        self.__db.table = conditions
        self.__view_records()


class SettingsF(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.__app = controller
        font_big = ('Tempus Sans ITC', 16, 'bold')
        self.config(bd=2, relief='groove')
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
        self.__trace()
        opt_main = tk.Frame(self, bd=2, relief='groove')
        opt_main.grid(row=0, column=0, padx=5, ipadx=0, pady=5, ipady=5, sticky='WEN')
        tk.Label(opt_main, text='Main Settings', font=font_big).grid(row=0, column=0, columnspan=2)
        tk.Label(opt_main, text='Save results', anchor='w', width=15).grid(row=1, column=0, sticky='EW', padx=5)
        tk.Button(opt_main, textvariable=self.__o_m_save, width=3, command=lambda: self.__change(self.__o_m_save, 'b')).grid(row=1, column=1)
        tk.Label(opt_main, text='Renew file', anchor='w').grid(row=2, column=0, sticky='EW', padx=5)
        tk.Button(opt_main, textvariable=self.__o_m_renew, width=3, command=lambda: self.__change(self.__o_m_renew, 'b')).grid(row=2, column=1)
        tk.Label(opt_main, text='Save to SQLite', anchor='w').grid(row=3, column=0, sticky='EW', padx=5)
        tk.Button(opt_main, textvariable=self.__o_m_sqlite, width=3, command=lambda: self.__change(self.__o_m_sqlite, 'b')).grid(row=3, column=1)
        opt_logs = tk.Frame(self, bd=2, relief='groove')
        opt_logs.grid(row=2, column=0, padx=5, ipadx=5, pady=5, ipady=5, sticky='WENS')
        tk.Label(opt_logs, text='Logs Settings', font=font_big).grid(row=0, column=0, columnspan=2)
        tk.Label(opt_logs, text='Save logs', anchor='w', width=15).grid(row=1, column=0, sticky='EW', padx=5)
        tk.Button(opt_logs, textvariable=self.__o_l_save, width=3, command=lambda: self.__change(self.__o_l_save, 'b')).grid(row=1, column=1)
        tk.Label(opt_logs, text='Log level', anchor='w').grid(row=2, column=0, sticky='EW', padx=5)
        tk.Button(opt_logs, textvariable=self.__o_l_lvl, width=3, command=lambda: self.__change(self.__o_l_lvl, 'lvl')).grid(row=2, column=1)
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
        opt_path = tk.Frame(self, bd=2, relief='groove', padx=5)
        opt_path.grid(row=2, column=1, padx=5, ipadx=0, pady=5, ipady=5, sticky='WEN')
        tk.Label(opt_path, text='Path Settings', font=font_big).grid(row=0, column=0, columnspan=2)
        tk.Label(opt_path, text='Directory', anchor='w').grid(row=1, column=0, sticky='EW')
        tk.Entry(opt_path, textvariable=self.__o_p_dir).grid(row=1, column=1)
        tk.Label(opt_path, text='result file', anchor='w').grid(row=2, column=0, sticky='EW')
        tk.Entry(opt_path, textvariable=self.__o_p_name).grid(row=2, column=1)
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
        self.row_id = tree.selection()[0]
        self.__tree = tree
        self.__db = db
        x, y = tree.winfo_pointerxy()
        x = tree.winfo_rootx() + 390
        self.geometry('+{}+{}'.format(x+5, y-10))
        self.overrideredirect(1)
        self.bind('<FocusOut>', lambda event: self.destroy())
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
        self.row_id = tree.selection()[0]
        self.row = tree.item(self.row_id)['values']
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
            self.__tree.set(self.row_id, 'jail', '')
            self.__db.data = ('jail', *self.row[0:4], date, None)
        self.destroy()


class DataBase:
    def __init__(self, db_connect=None, log_handler=None):
        self.__conn = None
        self.__cur = None
        if log_handler is None:
            def log_pass(*args, **kwargs):
                print('\33[91mDbLocal class ERROR: Log handler not found. \33[93mMSG:\33[0m', args[0].format(*args[2:]))
            self.__to_log = log_pass
        else:
            self.__to_log = log_handler

        if db_connect:
            self.open(db_connect)

    def open(self, pa):
        try:
            self.__conn = psycopg2.connect(host=pa['host'], database=pa['dbname'], user=pa['user'], password=pa['pwd'], connect_timeout=3.0)
        except psycopg2.Error as error:
            self.__to_log('DB ERROR {}', 1, str(error)[:-1], c1=Color.zero)
            self.__conn = None
            self.__cur = None
        else:
            self.__cur = self.__conn.cursor()
            self.__to_log('DB {} connected - {}', 3, pa['dbname'], 'OK', c1=Color.inf, c2=Color.ok)

    def select_sql(self, date):
        if not self.__conn:
            self.__to_log('Unable to select. Db connection error.', 2)
            return False
        date = date if (date and date.count('-') == 2 and len(date) in (10, 19)) else '2019-02-18'
        select = "SELECT " \
                 "upper(v.last_name), upper(v.first_name), upper(v.patronymic), to_char(v.birthdate, 'DD.MM.YYYY'), " \
                 "md5(concat(upper(v.last_name), upper(v.first_name), upper(v.patronymic), v.birthdate::date)), " \
                 "to_char(c.creation_date, 'YYYY-MM-DD hh24:mi:ss'), o.address, u.\"number\", " \
                 "CASE WHEN mia_check_result = 1 THEN 'МВД' ELSE 'ФССП' END " \
                 "FROM visitor_violation_checks AS c " \
                 "RIGHT JOIN visitors AS v ON c.visitor_id = v.id " \
                 "RIGHT JOIN court_objects AS o ON v.court_object_id = o.id " \
                 "RIGHT JOIN court_stations AS u ON v.court_station_id = u.id " \
                 "WHERE v.court_object_id not IN (173, 174) " \
                 "AND (mia_check_result = 1 OR fssp_check_result = 1) " \
                 f"AND v.creation_date > '{date}' ORDER BY v.creation_date DESC"
        self.__cur.execute(select)
        self.__to_log('SQL request return {} rows. Conditions: {}', 3, str(self.__cur.rowcount), select[632:-29].upper(), c1=Color.inf, c2=Color.info)
        return self.__cur.fetchall()

    def close(self):
        if self.__conn:
            db_info = self.__conn.get_dsn_parameters()
            self.__to_log('SQL Close. Host: {} DataBase: {}', 3, db_info['host'], db_info['dbname'])
            self.__conn.commit()
            self.__cur.close()
            self.__conn.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class DbLocal:
    def __init__(self, name='app', log_handler=None):
        if log_handler is None:
            def log_pass(*args, **kwargs):
                print('\33[91mDbLocal class ERROR: Log handler not found. \33[93mMSG:\33[0m', args[0].format(*args[2:]))
            self.__to_log = log_pass
        else:
            self.__to_log = log_handler
        name = name if isinstance(name, str) else 'app'
        self.__db = sqlite3.connect(name+'.db', timeout=5)
        self.__db.isolation_level = None
        self.__c = self.__db.cursor()
        self.__c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, first TEXT, name TEXT, second TEXT, dr DATE, c_sum CHAR(32))''')
        self.__c.execute('''CREATE TABLE IF NOT EXISTS visits (time TIMESTAMP, u_id INTEGER REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE, adr TEXT, court INTEGER, registry TEXT, comment TEXT, jail TEXT)''')
        self.__c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS visits_IDX ON visits (time, u_id)''')
        self.__c.execute('''CREATE TABLE IF NOT EXISTS sums (u_id INTEGER REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE, up_date DATE, sum REAL)''')
        self.__c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS sums_IDX ON sums (u_id, up_date)''')
        self.__u_sums_get()

    @property
    def table(self):
        return self.__table

    @table.setter
    def table(self, conditions):
        uniq = conditions.pop('uniq', False)
        c_sum = conditions.pop('c_sum', False)
        date_start = conditions.pop('start', False)
        date_end = conditions.pop('end', False)
        self.__to_log('Table conditions: uniq = {}, start = {}, end = {}, user = {}', 3, uniq, date_start, date_end, c_sum)
        vtime = 'min(v.time)' if uniq else 'v.time'
        first = f'''SELECT u."first", u.name, u.second, u.dr,  strftime('%d.%m.%Y %H:%M:%S', {vtime}), v.adr, v.court, v.registry, u.c_sum, v.comment, v.jail, (SELECT sum FROM (SELECT sum, MIN(ABS(strftime('%s',v.time) - strftime('%s', up_date))) AS xx FROM sums WHERE u_id = v.u_id)) FROM visits AS v LEFT JOIN users AS u ON u.id=v.u_id '''
        last = 'ORDER BY v.time DESC'
        last = 'GROUP BY u.id ' + last if uniq else last
        where = 'WHERE '
        if c_sum:
            where += f"u.c_sum = '{c_sum}' "
        if date_start:
            if c_sum:
                where += 'AND '
            where += 'v.time '
            where += f"BETWEEN '{date_start}' AND '{date_end}' " if date_end else f"> '{date_start}' "
        elif date_end:
            if c_sum:
                where += 'AND '
            where += f"v.time < '{date_end}' "
        if c_sum or date_start or date_end:
            first += where
        self.__table = self.__c.execute(first + last).fetchall()

    @property
    def visits(self):
        info = self.__c.execute('''SELECT SUM(vists), COUNT(*), SUM(fssp), ROUND(sum(nearest), 2) FROM (SELECT MIN(v.time), COUNT(*) AS vists, v.registry='ФССП' AS fssp, (SELECT sum FROM (SELECT sum, MIN(ABS(strftime('%s',v.time) - strftime('%s', up_date))) FROM sums WHERE u_id = v.u_id)) AS "nearest" FROM visits AS v LEFT JOIN users AS u ON u.id=v.u_id GROUP BY u.id)''').fetchone()
        info += self.__c.execute('''SELECT strftime('%Y-%m-%d %H:%M:%S', MAX(time)) FROM visits''').fetchone()
        self.__to_log('DB INFO Visits: {} Users: {}, FSSP: {}, PaySum: {}, Last visit: {}', 3, *info)
        return info

    @visits.setter
    def visits(self, array):
        if array and isinstance(array, list):
            for row in array:
                if len(row) == 9:
                    if row[4] in self.__u_sums:
                        self.__c.execute(f"SELECT id FROM users WHERE c_sum='{row[4]}'")
                        last_id = self.__c.fetchone()[0]
                    else:
                        self.__to_log('DB Add User: {} {} {} DR {} C_SUM {}', 3, *row[:5])
                        self.__c.execute("INSERT INTO users(first, name, second, dr, c_sum) VALUES (?, ?, ?, ?, ?)", (row[0].upper(), row[1].upper(), row[2].upper(), row[3], row[4]))
                        last_id = self.__c.lastrowid
                        self.__u_sums_get()
                    self.__c.execute("SELECT time, u_id FROM visits WHERE time=? AND u_id=?", (row[5], last_id))
                    if len(self.__c.fetchall()) > 0:
                        self.__to_log('This visit already exist. For: ID {}, Time {}', 2, last_id, row[5])
                    else:
                        self.__c.execute("INSERT INTO visits (time, u_id, adr, court, registry) VALUES (?, ?, ?, ?, ?)", (row[5], last_id, row[6], row[7], row[8]))
                else:
                    self.__to_log('Wrong format. Use tuple: (F, I, O, dr, control sum, time, adr, court, registry)', 2)

        else:
            self.__to_log('Use tuple to input visit: (F, I, O, dr, control sum, time, adr, court, registry)', 2)

    @property
    def data(self):
        last_update = self.__c.execute('''SELECT MAX(DATE(up_date)) FROM sums''').fetchone()[0]
        last_update = last_update if last_update else 0
        self.__c.execute(f'''SELECT u."first", u.name, u."second", u.dr, v.time FROM visits AS v LEFT JOIN users AS u ON u.id=v.u_id WHERE v.time > '{last_update}' GROUP BY u.id''')
        return self.__c.fetchall()

    @data.setter
    def data(self, data):
        if isinstance(data, tuple):
            self.__to_log('UPDATE user {} time {}. Value {} sets to {}', 3, data[1], data[5], data[0], data[6],
                          c1=Color.hl, c2=Color.hl, c3=Color.hl1, c4=Color.hl2)
            u_id = self.__c.execute('''SELECT id FROM users WHERE "first"=? AND name=? AND "second"=? AND dr=?''', (data[1].upper(), data[2].upper(), data[3].upper(), data[4])).fetchone()
            value = '' if not data[6] or data[6] == 'None' else data[6]
            if u_id:
                if data[0] == 'comment':
                    self.__c.execute(f"UPDATE visits SET comment='{value}' WHERE time='{data[5]}' AND u_id={u_id[0]}")
                elif data[0] == 'jail':
                    self.__c.execute(f"UPDATE visits SET jail='{value}' WHERE time='{data[5]}' AND u_id={u_id[0]}")
                elif data[0] == 'sum':
                    self.__c.execute(f"UPDATE sums SET sum={value} WHERE up_date='{data[5]}' AND u_id={u_id[0]}")
                    if self.__c.rowcount == 0:
                        self.__c.execute(f"INSERT INTO sums(u_id, up_date, sum) VALUES (?, ?, ?)", (*u_id, data[5], value))
                else:
                    self.__to_log('Wrong column name: {}', 2, data[0])
            else:
                self.__to_log('User not fount: {} {} {} {}', 2, *data[1:5])
        else:
            self.__to_log('Wrong data. Use tuple with format: (Column Name, F, I, O, dr, Time, Data to insert)', 2)

    def __u_sums_get(self):
        self.__c.execute('''SELECT c_sum FROM users''')
        self.__u_sums = [x[0] for x in self.__c.fetchall()]


class FSSP:
    def __init__(self, token='k51UxJdRmtyZ', pause=15, url='https://api-ip.fssprus.ru/api/v1.0/', log_handler=None):
        super().__init__()
        self.token = token
        self.url = url
        self.pause = int(pause) if int(pause) > 5 else 5
        self.region = 77
        self.__result = []
        if log_handler is None:
            def log_pass(*args, **kwargs):
                print('\33[91mFSSP class ERROR: Log handler not found. \33[93mMSG:\33[0m', args[0].format(*args[2:]))
            self.__to_log = log_pass
        else:
            self.__to_log = log_handler

    @staticmethod
    def __arr_check_doubles(arr):
        to_del = []
        n = len(arr)
        for x in range(n):
            if x in to_del:
                continue
            for y in range(n):
                if x == y:
                    continue
                elif y in to_del:
                    continue
                else:
                    if isinstance(arr[y], str):
                        if arr[x] == arr[y]:
                            to_del.append(y)
                    else:
                        typo = len(arr[y])
                        if typo == 2 and arr[x][0] == arr[y][0] and arr[x][1] == arr[y][1]:
                            to_del.append(y)
                        elif 3 < typo < 10:
                            if all([arr[x][0] == arr[y][0], arr[x][1] == arr[y][1],
                                    arr[y][2] == arr[x][2], arr[x][3] == arr[y][3]]):
                                to_del.append(y)
                        else:
                            to_del.append(y)
        arr_copy = arr[:]
        to_del.sort(reverse=True)
        for double in to_del:
            del arr_copy[double]
        return arr_copy, len(to_del)

    @property
    def arr(self):
        return self.__result

    @arr.setter
    def arr(self, array):
        if isinstance(array, list):
            self.__result = []
            arr, doubles_count = self.__arr_check_doubles(array)
            if doubles_count > 0:
                self.__to_log('Deleted doubles and errors from request. Count: {}', 3, doubles_count)
            if self.__uuid_get(arr):
                if self.__uuid_wait_finish():
                    self.__uuid_result()
            else:
                self.__to_log('Wait {} seconds. Spam defence', 3, self.pause)
                time.sleep(int(self.pause))

        else:
            self.__to_log('Input type not valid: {}. Use "List" instead.', 2, type(array))

    def __request_fssp(self, url, json):
        try:
            response = requests.get(url=url, json=json) if 'task' in json else requests.post(url=url, json=json)
        except requests.HTTPError as err:
            self.__to_log("HTTP fssp error. Exception: {}", 1, err)
            return False
        except requests.ConnectionError:
            self.__to_log("Error connection to fssp", 1)
            return False
        except requests.RequestException as err:
            self.__to_log("Exception fssp error. Exception: {}", 1, err)
            return False
        except Exception as err:
            self.__to_log("Unknown fssp error. Exception: {}", 1, err)
            return False
        try:
            js_resp = response.json()
        except Exception as err:
            self.__to_log("Response is not json. Exception: {}", 2, err)
            js_resp = {'exception': err, 'status': 'URL Error'}
        if response.status_code != 200:
            self.__to_log("Request error, CODE: {} Exception: {}", 1, response.status_code, js_resp["exception"],
                          c1=Color.inf, c2=Color.err)
            return False
        if js_resp['status'] != 'success':
            self.__to_log("Request error, Status: {} ", 2, js_resp['status'])
            return False
        return response

    def __uuid_get(self, array):
        if len(array) > 0:
            self.__to_log('Getting UUID for {} users...', 3, len(array))
        else:
            self.__to_log('Empty user list to get UUID', 2)
            return False
        reqst = {"token": self.token, "request": []}
        for elem in array:
            typo = len(elem)
            if isinstance(elem, str):
                self.__to_log('Add to fssp request: {}', 3, elem)
                subtask_js = {"type": 3, "params": {"number": elem}}
            elif typo == 2:
                self.__to_log('Add to fssp request: {} from {}', 3, *elem)
                subtask_js = {"type": 2, "params": {"name": elem[0], "address": elem[1], "region": self.region}}
            elif 3 < typo < 10:
                self.__to_log('Add to fssp request: {} {} {} {}', 3, *elem[0:4])
                subtask_js = {"type": 1,
                              "params": {"firstname": elem[1],
                                         "lastname": elem[0],
                                         "secondname": elem[2],
                                         "region": self.region,
                                         "birthdate": elem[3]}
                              }
            else:
                subtask_js = False
            reqst["request"].append(subtask_js)
        url = self.url + 'search/group'
        response = self.__request_fssp(url, reqst)
        if response:
            self.__uuid = response.json()['response']['task']
            self.__to_log('Successfully taken UUID {}', 3, response.json()['response']['task'])
            return True
        else:
            self.__to_log('Error while getting UUID.', 2)
            return False

    def __uuid_req(self, request_for='result'):
        status_arr = ('Finished', 'Not finished', 'Not started', 'Result error', 'Unknown error')
        if self.__uuid:
            url = self.url + 'result' if request_for == 'result' else self.url + 'status'
            params = {"token": self.token, "task": self.__uuid}
            response = self.__request_fssp(url, params)
            if response:
                js_resp = response.json()['response']
                if request_for == 'result':
                    return js_resp['result']
                else:
                    self.__to_log('For UUID {} Requests done {} Status: {}', 3, self.__uuid,
                                  js_resp['progress'], status_arr[js_resp['status']])
                    return js_resp['status']
        self.__to_log('UUID {} failure', 2, self.__uuid)
        return False

    def __uuid_wait_finish(self):
        self.__to_log('Getting result for UUID {}. Wait while finish!', 3, self.__uuid)
        while True:
            status = self.__uuid_req('status')
            if status is False or status > 2:
                return False
            elif status == 0:
                return True
            elif status in (1, 2):
                self.__to_log('Next request after {} seconds. Wait...', 3, self.pause)
                time.sleep(int(self.pause))
            else:
                self.__to_log('UUID status error.: {}', 1, status)

    def __uuid_result(self):
        result = []
        json_resp = self.__uuid_req()
        if json_resp is False:
            return False
        for sub_task in json_resp:
            calc = self.__violation_calc(sub_task)
            if sub_task['query']['type'] == 1:
                result.append([sub_task['query']['type'],
                               sub_task['query']['params']['lastname'],
                               sub_task['query']['params']['firstname'],
                               sub_task['query']['params']['secondname'],
                               sub_task['query']['params']['birthdate'],
                               calc])
            elif sub_task['query']['type'] == 2:
                result.append([sub_task['query']['type'], sub_task['query']['params']['name'], calc])
            elif sub_task['query']['type'] == 3:
                result.append([sub_task['query']['type'], sub_task['query']['params']['number'], calc])
        self.__result = result
        self.__to_log('FSSP Result ready', 3)
        return True

    @staticmethod
    def __violation_calc(sub_task):
        calc = 0.0
        regular = r'\d+\.?\d{1,2}?\sруб'
        if sub_task['status'] == 0:
            for violation in sub_task['result']:
                vio_str = re.findall(regular, violation['subject'])
                if vio_str:
                    for x in vio_str:
                        calc = round(calc + float(x[:-4]), 2)
        return calc


class CalPopup(tk.Label):
    not_current_is_nav = True
    __month_names = ('Zero Month Index', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май',
                     'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь')
    __week_names = ('Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс')

    def __init__(self, master, *args, **kwargs):
        super().__init__(master)
        for a in kwargs:
            print(a)
        self.__main = master
        self.__root = self.__main.winfo_toplevel()
        self.__day_vars = [tk.StringVar() for x in range(7*6) if x < 43]
        self.__curr_m_name = tk.StringVar()
        self.__curr_y_name = tk.StringVar()
        self.cal_ico = tk.PhotoImage(file='.\\img\\cal.png')
        btn = tk.Button(self.__main, command=self.__popup, cursor='hand2', image=self.cal_ico, **kwargs)
        btn.pack(side='left', fill='both', padx=1, ipadx=5)
        self.__bind_hover(btn)
        self.date = time.strftime("%Y-%m-%d", time.localtime())
        self.__main.date = self.date
        self.font_size = 14
        self.__styles_setter()

    @property
    def date(self):
        return '{}-{:02d}-{:02d}'.format(*self.__sel)

    @date.setter
    def date(self, value):
        try:
            time.strptime(value, '%Y-%m-%d')
            self.__sel = [int(n) for n in value.split('-')]
        except ValueError:
            print('\33[91mValue\33[93m', value, '\33[91merror. Must be a date format:\33[93m dd.mm.yyyy\33[0m')
        except TypeError:
            print('\33[91mValue\33[93m', value, '\33[91merror. Must be a string type format:\33[93m dd.mm.yyyy\33[0m')
        else:
            print('\33[94mSelecting date:\33[93m', self.date, '\33[0m')

    @property
    def font_size(self):
        return {'main': self.__font_c, 'weeks': self.__font_w, 'year': self.__font_y, 'nav': self.__font_n}

    @font_size.setter
    def font_size(self, size):
        if isinstance(size, int):
            print('\33[94mChanging font size to:\33[93m', size, '\33[0m')
            size = size if size <= 50 else 50
            self.__font_n = ('Console', size)
            self.__font_y = ('Console', int(size // 2.6))
            self.__font_c = ('Console', size)
            self.__font_w = ('Tempus Sans ITC', int(size // 1.6))
            self.__styles_setter()
        else:
            print('\33[91mSize must be int value. Using defaults.\33[0m')
        print('\33[94mUsing fonts:\33[0m')
        print('\33[93m{:5s} \33[92m{main}\33[93m\n{:5s} \33[92m{weeks}\33[93m\n{:5s} \33[92m{year}\33[93m\n{:5s} '
              '\33[92m{nav}\33[0m'.format(*self.font_size, **self.font_size), '\33[0m')

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
            style['background'] = '#999' if holiday else '#CCC'
            style['highlightbackground'] = '#666' if holiday else '#888'
        else:
            style['background'] = '#595959' if holiday else '#757575'
            style['highlightbackground'] = '#555' if holiday else '#555'
            style['fg'] = '#DDD'
        return style

    def __styles_setter(self):
        default = {'fg': '#111', 'bg': '#EEE', 'bd': 1, 'relief': 'raised', 'activebackground': '#090', 'activeforeground': '#AFA', 'highlightthickness': 0, 'highlightbackground': '#CCC'}
        self.__style_nav = {'font': self.__font_n, **default, 'pady': 5}
        self.__style_year = {'font': self.__font_y, **default, 'relief': 'flat', 'fg': '#222'}
        self.__style_week = {'font': self.__font_w, **default, 'width': 2}
        self.__style_cell = {'font': self.__font_c, **default, 'width': 2, 'cursor': 'hand2'}

    def __popup(self):
        top = tk.Toplevel()
        self.date = self.__main.date
        self.__curr = self.__sel[0:2]
        x = self.__main.winfo_rootx()
        y = self.__main.winfo_rooty() + self.__main.winfo_height()
        top.geometry('+{}+{}'.format(x, y))
        top.config(bd=0.4)
        top.resizable(False, False)
        top.overrideredirect(1)
        top.focus_force()
        top.bind('<FocusOut>', lambda event: top.destroy())
        top.bind('<Button-1>', self.__check_this_button)
        self.__nav_build(top)
        self.__matrix_create_frames(top)
        self.__matrix_change()

    def __nav_build(self, top):
        nav_frame = tk.Frame(top)
        nav_frame.pack(side='top', fill=tk.X)
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
        for i, week_day in enumerate(self.__week_names):
            week = tk.Label(cal_fr, self.__style_week, text=week_day)
            week.grid(row=0, column=i, ipadx=0, ipady=0, sticky='NSEW')
        self.__cells = [tk.Label(cal_fr, self.__style_cell, textvariable=self.__day_vars[i]) for i in range(42)]

    def __matrix_change(self):
        self.__curr_m_name.set(self.__month_names[self.__curr[1]])
        self.__curr_y_name.set(self.__curr[0])
        cal_array = list(TextCalendar(firstweekday=0).itermonthdays4(self.__curr[0], self.__curr[1]))
        row = 0
        for i, day in enumerate(cal_array):
            self.__day_vars[i].set(day[2])
            holiday = True if day[3] in (5, 6) else False
            what_month = 'current'
            if i < 7 and day[2] > 20:
                what_month = '<<<'
            elif i > 20 and day[2] < 7:
                what_month = '>>>'
            state = 'active' if self.__sel == [day[0], day[1], day[2]] else 'normal'
            cell, style = self.__cells[i], self.__get_cell_style(holiday, what_month)
            cell.config(style, state=state)
            row = row + 1 if day[3] == 0 else row
            cell.grid(row=row, column=day[3], ipadx=4, ipady=0)
            cell.what_m = what_month
            self.__bind_hover(cell)
        for i in range(len(cal_array), 42):
            self.__cells[i].grid_forget()

    def __check_this_button(self, event):
        ww = event.widget
        if 'label' not in str(ww):
            print('\33[91mGRID Error. Clicked not on {} widget\33[0m'.format(ww))
            return False
        try:
            ww.what_m
        except Exception as e:
            if ww['text'] in ('<<<', '>>>'):
                self.__curr_change(ww['text'])
            else:
                print('\33[94mYou press', ww, e, '\33[0m')
                return False
        if isinstance(ww['text'], int) and ww['text'] < 32:
            self.__curr_change(ww.what_m)
            if not self.not_current_is_nav or ww.what_m == 'current':
                self.__sel = [self.__curr[0], self.__curr[1], ww['text']]
                self.__date_selected()
                return True
        self.__matrix_change()

    def __curr_change(self, direction):
        if direction == '<<<':
            self.__curr = [self.__curr[0]-1, 12] if self.__curr[1] == 1 else [self.__curr[0], self.__curr[1]-1]
        elif direction == '>>>':
            self.__curr = [self.__curr[0]+1, 1] if self.__curr[1] == 12 else [self.__curr[0], self.__curr[1]+1]

    def __date_selected(self):
        self.date = '-'.join(map(str, self.__sel))
        self.__main.focus_force()
        self.__main.date = self.date


class DateEntry(tk.Label):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__day = tk.Entry(self, width=2, **kwargs)
        bg, self.hlbg = self.__day['bg'], self.__day['highlightbackground']
        self.__day.config(readonlybackground=bg, bg=self.hlbg)
        dot_dm = tk.Label(self, text='.', **kwargs)
        dot_dm.config(bg=self.hlbg)
        self.__month = tk.Entry(self, width=2, readonlybackground=bg, **kwargs)
        self.__month.config(readonlybackground=bg, bg=self.hlbg)
        dot_my = tk.Label(self, text='.', **kwargs)
        dot_my.config(bg=self.hlbg)
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
        return '{}-{:02d}-{:02d}'.format(y, m, d)

    @date.setter
    def date(self, value):
        try:
            y, m, d = value.split('-')
        except Exception as e:
            print('Value not a date format dd.mm.yyyy Change it:', value, e)
        else:
            self.__day.delete(0, tk.END)
            self.__month.delete(0, tk.END)
            self.__year.delete(0, tk.END)

            self.__day.insert(0, d)
            self.__month.insert(0, m)
            self.__year.insert(0, y)

    def __day_part_detect(self, widget):
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
        ww = event.widget
        ww.config(state='readonly')
        key = event.keysym
        v = ww.get()
        wth = ww['width']
        cur_pos = ww.index('insert')
        selected = ww.selection_present()
        part = self.__day_part_detect(ww)
        if selected and key.isdigit():
            ww.config(state='normal')
        elif key == 'BackSpace':
            if cur_pos == 0:
                if part[0]:
                    part[0].focus()
                    self.__backspace(part[0])
            else:
                ww.config(state='normal')
        elif key == 'Delete':
            if cur_pos >= wth or (cur_pos == 0 and len(v) == 0):
                if part[1]:
                    part[1].focus()
                    part[1].icursor(0)
                    self.__delete(part[1])
            else:
                ww.config(state='normal')
        elif key.isdigit():
            if len(v) >= wth:
                if cur_pos >= wth:
                    if part[1]:
                        part[1].focus()
                        part[1].icursor(0)
                        if len(part[1].get()) >= part[1]['width']:
                            self.__delete(part[1])
                            part[1].insert(0, key)
                        else:
                            part[1].insert(0, key)
                    else:
                        ww.config(state='normal')
                        self.__backspace(ww)
                else:
                    ww.config(state='normal')
                    self.__delete(ww)
            elif len(v) + 1 >= wth:
                ww.config(state='normal')
                if part[1]:
                    part[1].focus()
                    if len(part[1].get()) == part[1]['width']:
                        part[1].selection_range(0, 'end')
            else:
                ww.config(state='normal')
        elif key == 'Left' and cur_pos == 0 and part[0]:
            part[0].focus()
        elif key == 'Right' and part[1] and (cur_pos >= wth or (cur_pos == 0 and len(v) == 0)):
            part[1].focus()
        elif key in ('Alt_R', 'Alt_L', 'Control_L', 'Control_R'):
            pass

    def _release(self, event):
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
        if y > 999 and (1900 > y or y > 2100):
            self.__year.config(bg='#F77')
        else:
            self.__year.config(bg=self.hlbg)


class Excel:
    def __init__(self, f_name='test.xlsx', log_handler=None):
        self.f_name = f_name
        self.__fmt_h_def = {'bold': 1, 'align': 'center', 'valign': 'vcenter', 'border': 1}
        if log_handler is None:
            def log_pass(*args, **kwargs):
                print('\33[91mExcel class ERROR: Log handler not found. \33[93mMSG:\33[0m', args[0].format(*args[2:]))
            self._to_log = log_pass
        else:
            self._to_log = log_handler
        if self.__workbook_can_create():
            self.__workbook = xlsxwriter.Workbook(self.f_name)
            self._to_log('WorkBook {} created.', 3, self.f_name)

    def data_from_db(self, conditions=None):
        db = DbLocal('fssp', self._to_log)
        db.table = conditions if conditions and isinstance(conditions, dict) else {'uniq': False}
        self.data(db.table)
        if not conditions:
            db.table = {'uniq': True}
            self.data(db.table, 'ruk')
        self.__workbook.close()

    def data(self, array, sheet='main'):
        if isinstance(array, list) and len(array) > 0:
            if self.__workbook_can_create():
                fmt_tmp = {'bold': 1, 'align': 'right', 'valign': 'vcenter', 'border': 1, 'bg_color': '#77BBF0'}
                fmt_h2_money = self.__workbook.add_format({'num_format': "# ### ### ##0.00 ₽", **fmt_tmp})
                fmt_hl_red = self.__workbook.add_format({'bg_color': '#FFCCCC', 'font_color': '#FF0000'})
                fmt_hl_green = self.__workbook.add_format({'bg_color': '#CCFFCC', 'font_color': '#005500'})
                fmt_hl_green2 = self.__workbook.add_format({'bg_color': '#CCFFCC'})
                fmt_hl_yellow = self.__workbook.add_format({'bg_color': '#FFFF00'})
                fmt_h2 = self.__workbook.add_format({'bg_color': '#77BBF0', **self.__fmt_h_def})
                fmt_date = self.__workbook.add_format({'num_format': 'dd.mm.yyyy h:mm', 'border': 1, 'align': 'left', 'indent': 1})
                fmt_adr = self.__workbook.add_format({'indent': 1, 'border': 1})
                fmt_center = self.__workbook.add_format({'align': 'center', 'border': 1})
                fmt_money = self.__workbook.add_format({'num_format': '# ### ### ##0.00 ₽', 'border': 1})
                fmt_bd = self.__workbook.add_format({'border': 1})

                def add_row(idx, data):
                    date, adr, court, reg, c_sum, comm, jail, pay_sum = data
                    date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S")
                    comm = '' if not comm or comm == 'None' else comm
                    jail = '' if not jail or jail == 'None' or (sheet == 'ruk' and reg == 'ФССП') else jail
                    pay_sum = float(pay_sum) if pay_sum else 0
                    if sheet == 'main':
                        self.__main_p.write_datetime(idx, 0, date, fmt_date)
                        self.__main_p.write_string(idx, 1, adr, fmt_adr)
                        self.__main_p.write_number(idx, 2, int(court), fmt_center)
                        self.__main_p.write_string(idx, 3, reg, fmt_center)
                        self.__main_p.write_string(idx, 4, c_sum, fmt_bd)
                        self.__main_p.write_string(idx, 5, comm, fmt_bd)
                        self.__main_p.write_string(idx, 6, jail, fmt_center)
                        self.__main_p.write_number(idx, 7, pay_sum, fmt_money)
                    elif sheet == 'ruk':
                        self.__ruk_p.write_datetime(idx, 0, date, fmt_date)
                        self.__ruk_p.write_string(idx, 1, adr, fmt_adr)
                        self.__ruk_p.write_number(idx, 2, int(court), fmt_center)
                        self.__ruk_p.write_string(idx, 3, reg, fmt_center)
                        self.__ruk_p.write_string(idx, 4, comm, fmt_bd)
                        self.__ruk_p.write_string(idx, 5, jail, fmt_center)
                        self.__ruk_p.write_number(idx, 6, pay_sum, fmt_money)
                self.__sheet_create(sheet)
                if sheet == 'main':
                    obj = self.__main_p
                    row_idx = 2
                    obj.conditional_format('D3:D10000', {'type': 'cell', 'criteria': '==', 'value': '"МВД"', 'format': fmt_hl_red})
                    obj.conditional_format('D3:D10000', {'type': 'cell', 'criteria': '==', 'value': '"ФССП"', 'format': fmt_hl_green})
                    obj.conditional_format('E3:E10000', {'type': 'formula', 'criteria': '=COUNTIF($E$3:$E$10000, E3)>1', 'format': fmt_hl_red})
                    obj.conditional_format('G3:G10000', {'type': 'cell', 'criteria': '==', 'value': '"ЗАДЕРЖАН"', 'format': fmt_hl_red})
                    obj.conditional_format('H3:H10000', {'type': 'formula', 'criteria': '=FREQUENCY(MATCH(E3:$E$21,E3:$E$21,0),MATCH(E3:$E$21,E3:$E$21,0)) = COUNTIF($E$3:$E$10002, E3)', 'format': fmt_hl_green2})
                    obj.conditional_format('H3:H10000', {'type': 'formula', 'criteria': '=COUNTIF($E$3:$E$10000, E3)>1', 'format': fmt_hl_yellow})
                else:
                    obj = self.__ruk_p
                    row_idx = 4
                    obj.conditional_format('D5:D10000', {'type': 'cell', 'criteria': '==', 'value': '"МВД"', 'format': fmt_hl_red})
                    obj.conditional_format('D5:D10000', {'type': 'cell', 'criteria': '==', 'value': '"ФССП"', 'format': fmt_hl_green})
                    obj.conditional_format('F5:F10000', {'type': 'cell', 'criteria': '==', 'value': '"ЗАДЕРЖАН"', 'format': fmt_hl_red})
                for row_add in array:
                    if len(row_add) == 8:
                        add_row(row_idx, row_add)
                        row_idx += 1
                    elif len(row_add) == 12:
                        add_row(row_idx, row_add[4:])
                        row_idx += 1
                    else:
                        self._to_log('Error adding row: {}', 2, row_add)
                if sheet == 'main':
                    obj.write(1, 0, 'ИТОГО', fmt_h2)
                    obj.write(1, 1, '=CONCATENATE("Нарушителей: ", COUNT(C:C))', fmt_h2)
                    obj.write(1, 2, '', fmt_h2)
                    obj.write(1, 3, '=CONCATENATE("ФССП: ",COUNTIF(D3:D10000,"ФССП")," МВД: ",COUNTIF(D3:D10000,"МВД"))', fmt_h2)
                    obj.write(1, 4, '', fmt_h2)
                    obj.write(1, 5, '', fmt_h2)
                    obj.write(1, 6, '=COUNTIF(G3:G10000, "ЗАДЕРЖАН")', fmt_h2)
                    obj.write(1, 7, f'=SUM(IF(FREQUENCY(MATCH(E3:E{row_idx}, E3:E{row_idx}, 0), MATCH(E3:E{row_idx}, E3:E{row_idx}, 0))>0, H3:H{row_idx}, 0))', fmt_h2_money)
                else:
                    obj.write(3, 0, 'ИТОГО', fmt_h2)
                    obj.write(3, 1, '=CONCATENATE("Нарушителей: ", COUNT(C:C))', fmt_h2)
                    obj.write(3, 2, '', fmt_h2)
                    obj.write(3, 3, '=CONCATENATE("ФССП: ",COUNTIF(D5:D10000,"ФССП")," МВД: ",COUNTIF(D5:D10000,"МВД"))', fmt_h2)
                    obj.write(3, 4, '', fmt_h2)
                    obj.write(3, 5, '=COUNTIF(F5:F10000, "ЗАДЕРЖАН")', fmt_h2)
                    obj.write(3, 6, f'=SUM(G5:G{row_idx})', fmt_h2_money)

    def __workbook_can_create(self):
        try:
            f_tmp = open(self.f_name, 'w')
        except Exception as err:
            self._to_log('{}', 1, err)
            return False
        else:
            f_tmp.close()
        return True

    def __sheet_create(self, name='main'):
        fmt_h1 = self.__workbook.add_format({'bg_color': '#FEE0D0', **self.__fmt_h_def})
        fmt_big = self.__workbook.add_format({'font_size': '20', 'align': 'center', 'valign': 'vcenter'})
        if name == 'main':
            self.__main_p = self.__workbook.add_worksheet('Отчет')
            self.__main_p.set_column('A:A', 17)
            self.__main_p.set_column('B:B', 47)
            self.__main_p.set_column('C:C', 7.3)
            self.__main_p.set_column('D:D', 18)
            self.__main_p.set_column('E:E', 36)
            self.__main_p.set_column('F:F', 58)
            self.__main_p.set_column('G:G', 11.3)
            self.__main_p.set_column('H:H', 17)
            self.__main_p.set_row(0, 25)
            self.__main_p.set_row(1, 25)
            self.__main_p.freeze_panes(2, 0)
            self.__main_p.set_default_row(15)
            self.__main_p.write('A1', 'ДАТА', fmt_h1)
            self.__main_p.write('B1', 'АДРЕС', fmt_h1)
            self.__main_p.write('C1', 'Участок', fmt_h1)
            self.__main_p.write('D1', 'РЕЕСТР', fmt_h1)
            self.__main_p.write('E1', 'Контрольная Сумма', fmt_h1)
            self.__main_p.write('F1', 'Комментарий', fmt_h1)
            self.__main_p.write('G1', 'Задержаний', fmt_h1)
            self.__main_p.write('H1', 'Сумма взысканий', fmt_h1)
        else:
            self.__ruk_p = self.__workbook.add_worksheet('Для руководства')
            self.__ruk_p.set_column('A:A', 17)
            self.__ruk_p.set_column('B:B', 47)
            self.__ruk_p.set_column('C:C', 7.3)
            self.__ruk_p.set_column('D:D', 18)
            self.__ruk_p.set_column('E:E', 58)
            self.__ruk_p.set_column('F:F', 11.3)
            self.__ruk_p.set_column('G:G', 17)
            self.__ruk_p.set_row(0, 21.75)
            self.__ruk_p.set_row(1, 21.75)
            self.__ruk_p.set_row(2, 25)
            self.__ruk_p.set_row(3, 25)
            self.__ruk_p.freeze_panes(4, 0)
            self.__ruk_p.set_default_row(15)
            self.__ruk_p.merge_range('A1:G1', 'С П Р А В К А', fmt_big)
            self.__ruk_p.merge_range('A2:G2', f'по состоянию на {datetime.strftime(datetime.today(), "%d.%m.%Y")} года.', fmt_big)
            self.__ruk_p.write('A3', 'ДАТА', fmt_h1)
            self.__ruk_p.write('B3', 'АДРЕС', fmt_h1)
            self.__ruk_p.write('C3', 'Участок', fmt_h1)
            self.__ruk_p.write('D3', 'РЕЕСТР', fmt_h1)
            self.__ruk_p.write('E3', 'Комментарий', fmt_h1)
            self.__ruk_p.write('F3', 'Задержаний', fmt_h1)
            self.__ruk_p.write('G3', 'Сумма взысканий', fmt_h1)
        self._to_log('Sheet "{}" created.', 3, name)


if __name__ == '__main__':
    app = App()
    app.mainloop()