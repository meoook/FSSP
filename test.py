import configparser
import requests
import time
import re
import psycopg2
import os
import tkinter as tk
from tkinter import ttk
'''
COLORS
INFO    93
ERROR   33
CRIT    31
OK      94
FAIL    91
'''


class Fssp:
    def __init__(self):
        super().__init__()
        self.get_config()
        self.save_cfg()

    # CONFIG
    def get_config(self):
        self.cfg = configparser.ConfigParser()
        config = configparser.ConfigParser()
        if config.read('config.ini'):
            print('Reading config file\33[94m config.ini\33[0m -\33[93m OK\33[0m')
        else:
            print('Reading config file\33[94m config.ini\33[0m -\33[91m Fail\33[0m')
        self.cfg.add_section('OPTIONS')     # OPTIONS CONFIG
        self.cfg.set('OPTIONS', 'PAUSE', config.get('OPTIONS', 'PAUSE', fallback='15'))
        self.cfg.set('OPTIONS', 'SAVE_RESULT', config.get('OPTIONS', 'SAVE_RESULT', fallback='True'))
        self.cfg.set('OPTIONS', 'RES_FILE_RENEW', config.get('OPTIONS', 'RES_FILE_RENEW', fallback='True'))
        self.cfg.set('OPTIONS', 'RES_FILE_HEAD', config.get('OPTIONS', 'RES_FILE_HEAD',
                    fallback='Время, Адрес, Участок, Реестр, Контрольная сумма, Комментарий, Задержан, Сумма штрафов'))
#       RES_FILE_HEAD = [v.strip() for v in config['OPTIONS']['RES_FILE_HEAD'].split(',')]
        self.cfg.add_section('PATH')        # PATH CONFIG
        self.cfg.set('PATH', 'DIR', config.get('PATH', 'DIR', fallback='C:\\tmp\\'))
        self.cfg.set('PATH', 'RES_FILENAME', config.get('PATH', 'RES_FILENAME', fallback='fssp.csv'))
        self.cfg.add_section('POSTGRES')  # PG_SQL CONFIG
        self.cfg.set('POSTGRES', 'PG_HOST', config.get('POSTGRES', 'PG_HOST', fallback='172.17.75.4'))
        self.cfg.set('POSTGRES', 'PG_DB_NAME', config.get('POSTGRES', 'PG_DB_NAME', fallback='ums'))
        self.cfg.set('POSTGRES', 'PG_USER', config.get('POSTGRES', 'PG_USER', fallback='fssp_read'))
        self.cfg.set('POSTGRES', 'PG_PWD', config.get('POSTGRES', 'PG_PWD', fallback='1234'))
        self.cfg.add_section('FSSP.RU')     # FSSP CONFIG
        self.cfg.set('FSSP.RU', 'TOKEN', config.get('FSSP.RU', 'TOKEN', fallback='k51UxJdRmtyZ'))
        self.cfg.set('FSSP.RU', 'BASE_URL', config.get('FSSP.RU', 'BASE_URL',
                                                       fallback='https://api-ip.fssprus.ru/api/v1.0/'))
        self.cfg.set('FSSP.RU', 'GROUP_URL', config.get('FSSP.RU', 'GROUP_URL', fallback='search/group'))
        self.cfg.set('FSSP.RU', 'STATUS_URL', config.get('FSSP.RU', 'STATUS_URL', fallback='status'))
        self.cfg.set('FSSP.RU', 'RESULT_URL', config.get('FSSP.RU', 'RESULT_URL', fallback='result'))
        self.cfg.add_section('LOGS')      # LOG CONFIG
        self.cfg.set('LOGS', 'LOG_TO_FILE', config.get('LOGS', 'LOG_TO_FILE', fallback='True'))
        self.cfg.set('LOGS', 'LOG_LVL', config.get('LOGS', 'LOG_LVL', fallback='3'))
#       log_file_name = PATH['DIR'] + 'Logs\\fssp_' + time.strftime("%d.%m.%y", time.localtime()) + '.log'
        if not configparser.ConfigParser().read('config.ini'):
            print('Creating config file\33[94m config.ini\33[0m with default settings')
        self.save_cfg()

    def save_cfg(self):
        with open('config.ini', 'w') as cfg_file:
            self.cfg.write(cfg_file)


class AppWindow:
    def __init__(self, master):
        super().__init__()
        # Отобразить встроенные стили
        print(ttk.Style().theme_names())
        ttk.Style().theme_use('default')

        self.add_img = tk.PhotoImage(file='.\img\windows.gif')
        self.init_main(master)
        self.mmm = root

    def init_main(self, mm):
        self.toolbar = tk.Frame(mm, bg='#d3d3d3', bd=2)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        btn_open_dialog = tk.Button(self.toolbar, text='Add position', command=self.gui_quit, bg="#f4f4f4", bd=0,
                                    compound=tk.TOP, image=self.add_img)
        btn_open_dialog.pack(side=tk.LEFT)

        canvas = tk.Canvas(mm, width=1035, height=155, bg='#002')
        canvas.pack(side='top', expand=tk.YES)
        canvas.place(y=285)

        [canvas.create_line(10+x*20, 10, 10+x*20, 150, width=1, fill='#191938') for x in range(52)]
        [canvas.create_line(10, 10+y*20, 1030, 10+y*20, width=1, fill='#191938') for y in range(8)]

        canvas.create_line(20, 80, 1020, 80, width=1, fill='#FFF', arrow=tk.LAST)
        canvas.create_text(40, 70, text='Пульс', fill='#FFF')

    def gui_quit(self):
        self.mmm.quit()


if __name__ == '__main__':
    app = Fssp()
    print(app.cfg['POSTGRES']['PG_HOST'])
    root = tk.Tk()
    main_window = AppWindow(root)
    root.title("My GUI Test")
    root.geometry('1040x450+300+200')
    root.resizable(False, False)
    root.mainloop()

