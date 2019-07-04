import configparser
import requests
import time
import re
import psycopg2
import os


DEFAULTS = {
'PAUSE': '15',                # Интервал в секундах между запросами (в случае если task не выполнена)
'SAVE_RESULT': True,          # Сохранять результат в файл
'RES_FILE_RENEW': True,       # Обновлять файл с результатами или дописывать в конец файла
'RES_FILE_HEAD': 'Время, Адрес, Участок, Реестр, Контрольная сумма, Комментарий, Задержан, Сумма штрафов',
# PATH CONFIG
'DIR': 'C:\\tmp\\',           # Основная папка
'RES_FILENAME': 'fssp.csv',   # Куда будут сохрянаться результаты
# LOG CONFIG
'LOG_TO_FILE': True,          # Сохранять в файл
'LOG_LVL': 3,                 # 1 - Critical, 2 - data err, 3 - info(all))
# PG_SQL CONFIG
'PG_HOST': '172.17.75.4',
'PG_USER': 'fssp_read',
'PG_PWD': '1234',
'PG_DB_NAME': 'ums',
# FSSP CONFIG
'TOKEN': 'k51UxJdRmtyZ',      # Токен, ключик без которого ничего не работает
'BASE_URL': 'https://api-ip.fssprus.ru/api/v1.0/',
'GROUP_URL': 'search/group',  # POST мультипоиск ФИЗ\ЮР\ИП
'STATUS_URL': 'status',       # GET на получение статуса
'RESULT_URL': 'result'}       # GET на получение результата

print(DEFAULTS['BASE_URL']+DEFAULTS['GROUP_URL'])

class Fssp:
    def __init__(self):
        super().__init__()
        self.get_config()

    def get_config(self):
        global OPTIONS, RES_FILE_HEAD, PATH, LOGING, POSTGRESQL, FSSP
        config = configparser.ConfigParser(defaults=DEFAULTS, allow_no_value=False, empty_lines_in_values=False)
        if config.read('config.ini'):
            print('Reading config file\33[93m config.ini\33[0m -\33[32m OK\33[0m')

            if config.has_section('OPTIONS'):
                OPTIONS = config['OPTIONS']
            else:
                config.add_section('OPTIONS')

            config.get('OPTIONS', 'Pause', fallback='TEST')

#            if not config.get('OPTIONS', 'Pause') or not config['OPTIONS'].getint('Pause'):
#                config.set('OPTIONS', 'Pause', DEFAULTS['PAUSE'])
            RES_FILE_HEAD = [v.strip() for v in config['OPTIONS']['RES_FILE_HEAD'].split(',')]
            PATH = config['PATH']
            POSTGRESQL = config['POSTGRESQL']
            FSSP = config['FSSP.RU']
            LOGING = config['LOGING']
            LOG_FILE_NAME = PATH['DIR'] + 'logs\\fssp_' + time.strftime("%d.%m.%y", time.localtime()) + '.log'
            config.set('LOGING', 'LOG_FILE_NAME', LOG_FILE_NAME)
        else:   # Default settings
            print('Reading config file\33[93m config.ini\33[0m -\33[91m Fail\33[0m')
            print('Creating config file with default settings.')
            config['OPTIONS'] = {'PAUSE': '15',
                                 'SAVE_RESULT': 'True',
                                 'RES_FILE_RENEW': 'True',
                                 'RES_FILE_HEAD': 'Время, Адрес, Участок, Реестр, Контрольная сумма,'
                                                  'Комментарий, Задержан, Сумма штрафов'}
            config['PATH'] = {'DIR': 'C:\\tmp\\',
                              'RES_FILENAME': 'fssp.csv'}
            config['LOGING'] = {'LOG_TO_FILE': 'True',
                                'LOG_LVL': '3'}
            config['POSTGRESQL'] = {'PG_HOST': '172.17.75.4',
                                    'PG_USER': 'fssp_read',
                                    'PG_PWD': '1234',
                                    'PG_DB_NAME': 'ums'}
            config['FSSP.RU'] = {'TOKEN': 'k51UxJdRmtyZ',
                                 'BASE_URL': 'https://api-ip.fssprus.ru/api/v1.0/',
                                 'GROUP_URL': 'search/group',
                                 'STATUS_URL': 'status',
                                 'RESULT_URL': 'result'}
            with open('config.ini', 'w') as ConfigFile:
                config.write(ConfigFile)
            self.get_config()



if __name__ == '__main__':
    app = Fssp()
    print(OPTIONS['Pause'])
