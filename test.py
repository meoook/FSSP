import configparser
import time


def get_config():
    global OPTIONS, RES_FILE_HEAD, PATH, LOGING, POSTGRESQL, FSSP
    config = configparser.ConfigParser()
    if config.read('config.ini'):
        print('Reading config file\33[93m config.ini\33[0m -\33[32m OK\33[0m')
        OPTIONS = config['OPTIONS']
        RES_FILE_HEAD = [v.strip() for v in config['OPTIONS']['RES_FILE_HEAD'].split(',')]
        PATH = config['PATH']
        POSTGRESQL = config['POSTGRESQL']
        FSSP = config['FSSP.RU']
        LOGING = config['LOGING']
        LOG_FILE_NAME = PATH['DIR'] + 'logs\\fssp_' + time.strftime("%d.%m.%y", time.localtime()) + '.log'
        config.set('LOGING', 'LOG_FILE_NAME', LOG_FILE_NAME)
        return False
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
        get_config()


get_config()
