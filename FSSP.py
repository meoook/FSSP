import requests
import time
import re
import psycopg2
import os


''' CONFIG '''
new_param = 'new param'
# PROGRAM CONFIG4
PAUSE = 15                  # Интервал в секундах между запросами (в случае если task не выполнена)
PARSE_FILE = False          # Будет ли парсится файл? (FILENAME)
SAVE_RESULT = True          # Сохранять результат в файл
TAB_SEPARATOR = False       # Разделитель в файле c результатами (знак табуляции или ; [copy from notepad or xlsx])
RES_FILE_RENEW = True       # Обновлять файл с результатами или дописывать в конец файла
RES_FILE_HEAD = ['Время', 'Адрес', 'Участок', 'Реестр', 'Контрольная сумма', 'Комментарий', 'Задержан', 'Сумма штрафов']
# PATH CONFIG
DIR = 'C:\\tmp\\'           # Основная папка
RES_FILENAME = 'fssp.csv'   # Куда будут сохрянаться результаты
REQ_FILENAME = 'fssp.txt'   # Файл который будет парситься для запроса (не используется)
# LOG CONFIG
LOG_DIR = 'Logs'            # Папка для логов
LOG_ECHO = True             # Вывод логов на экран
LOG_TO_FILE = True          # Сохранять в файл
LOG_LVL = 1                 # 1 - Critical, 2 - data err, 3 - info(all))
LOG_FILE_NAME = DIR + LOG_DIR + '\\' + 'fssp_' + time.strftime("%d.%m.%y", time.localtime()) + '.log'
# PG_SQL CONFIG
PG_HOST = '172.17.75.4'
PG_USER = 'fssp_read'
PG_PWD = '1234'
PG_DB_NAME = 'ums'
# HOME
PG_HOST_HOME = 'localhost'
PG_USER_HOME = 'postgres'
PG_PWD_HOME = '111'
PG_DB_NAME_HOME = 'skuns'
# FSSP CONFIG
TOKEN = 'k51UxJdRmtyZ'      # Токен, ключик без которого ничего не работает
BASE_URL = 'https://api-ip.fssprus.ru/api/v1.0/'
FIZ_URL = 'search/physical' # GET поиск по ФИО + ДР (не используется)
IP_URL = 'search/ip'        # GET поиск по Номеру ИП (не используется)
GROUP_URL = 'search/group'  # POST мультипоиск ФИЗ\ЮР\ИП
STATUS_URL = 'status'       # GET на получение статуса
RESULT_URL = 'result'       # GET на получение результата


# FUNCTIONS
# Проверка всех путей like __init__ ; сделать через try - вдруг прав нет
def chk_paths():
    global SAVE_RESULT, LOG_TO_FILE
    print('Checking folders structure...')

    if not os.path.isdir(DIR):  # Проверка основной папки
        print("Creating main folder", DIR)
        os.makedirs(DIR)
    else:
        print('Main folder', DIR, 'exist - OK')
    if SAVE_RESULT and (not os.path.isfile(DIR + RES_FILENAME) or RES_FILE_RENEW):
        try:
            filo = open(DIR + RES_FILENAME, "w")
            sep = "\t" if TAB_SEPARATOR else ";"
            filo.write(sep.join(RES_FILE_HEAD) + '\n')
            filo.close()
            print("Creating result file", DIR + RES_FILENAME)
        except IOError as err:
            print('Error open file:', DIR + RES_FILENAME, 'Err:', err)
            print('Set SAVE_RESULT = False')
            SAVE_RESULT = False
    else:
        print("Result file", DIR + RES_FILENAME, 'exist - OK')

    if LOG_TO_FILE and not os.path.isdir(DIR + LOG_DIR):  # Если логирование включено
        try:
            os.makedirs(DIR + LOG_DIR)
        except:
            print('Error creating folder', DIR + LOG_DIR)
            print('Set LOG_TO_FILE = False')
            LOG_TO_FILE = False
        else:
            print("Creating log folder", DIR + LOG_DIR)
    else:
        print('Log folder', DIR + LOG_DIR, 'exist - OK')

    if LOG_TO_FILE and not os.path.isfile(LOG_FILE_NAME):
        try:
            filo = open(LOG_FILE_NAME, "w")
            filo.write(time.strftime("%d.%m.%y %H:%M:%S", time.localtime())+': Created file log '+LOG_FILE_NAME+'\n')
            print('Creating log file', LOG_FILE_NAME)
        except:
            print('Error creating folder', DIR + LOG_DIR)
            print('Set LOG_TO_FILE = False')
            LOG_TO_FILE = False

    else:
        print('Log file', LOG_FILE_NAME, 'exist - OK')

    if PARSE_FILE:  # Если берем данные из файла
        if not os.path.isfile(DIR + REQ_FILENAME):
            print('ERROR: No file to parse', DIR + REQ_FILENAME)
            return False
        else:
            print('File to parse', DIR + REQ_FILENAME, 'exist - OK')


# Записать сообщение в лог файл
def to_log(msg: str, deep_lvl: int = 3):
    if msg is False:
        msg = 'Try to put empty message in log'
        deep_lvl = 1
    if deep_lvl == 1:
        msg = '[CRIT] ' + msg
    elif deep_lvl == 2:
        msg = '[ERR] ' + msg
    else:
        msg = '[INFO] ' + msg
    msg = time.strftime("%d.%m.%y %H:%M:%S", time.localtime()) + ' ' + msg
    if LOG_ECHO:
        print(msg)
    if LOG_TO_FILE:
        if LOG_LVL >= deep_lvl:
            with open(LOG_FILE_NAME, "a") as filo:
                filo.write(msg + '\n')


# Записываем результат в файл
def write_csv(xlsx_array):
    try:
        filo = open(DIR + RES_FILENAME, "a")
        for row in xlsx_array:
            sep = "\t" if TAB_SEPARATOR else ";"
            filo.write(sep.join(map(str, row)) + "\n")
        filo.close()
    except OSError as err:
        to_log('OS error: {0}'.format(err), 1)
        return False
    except Exception as ex:
        to_log('Error write file: ' + str(ex), 1)
        return False
    else:
        to_log('Success write results to file.')


# SQL: Запрос нарушителей за\с сегодня\дату
def sql_req_home(date='xx', znak='eq'):
    conn = None
    rows = []
    try:
        conn = psycopg2.connect(host=PG_HOST_HOME,
                                user=PG_USER_HOME,
                                password=PG_PWD_HOME,
                                database=PG_DB_NAME_HOME)
        cur = conn.cursor()
        # Делаем SELECT
        select = "SELECT upper(lastname), upper(firstname), upper(secondname), to_char(birthday, 'DD.MM.YYYY'), " \
                 "to_char(creation_date, 'DD.MM.YYYY hh24:mi:ss'), court_adr, court_numb, reestr, " \
                 "md5(concat(upper(lastname), upper(firstname), upper(secondname), to_char(birthday, 'DD.MM.YYYY'))) " \
                 "FROM fssp as v WHERE creation_date::date "
        select += "=" if znak == 'eq' else ">="
        select += "current_date " if date == 'xx' else "'" + date + "'"  # Нужна проверочка - что date соответсвует формату
        cur.execute(select)
        rows = cur.fetchall()  # Return
        # TO LOG?: cur.rowcount
        cur.close()
    except psycopg2.Error as error:
        to_log('SQL ERROR: ' + str(error), 1)  # SQL ERROR select
    finally:
        if conn is not None:
            conn.close()
        return rows


# SQL: Запрос нарушителей за\с сегодня\дату
def sql_req(date='xx', znak='eq'):
    # Нужна проверочка - что date соответсвует формату
    conn = None
    rows = []
    try:
        conn = psycopg2.connect(host=PG_HOST, user=PG_USER, password=PG_PWD, database=PG_DB_NAME)
        cur = conn.cursor()
        # Делаем SELECT
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
        select += "=" if znak == 'eq' else ">="
        select += "CURRENT_DATE " if date == 'xx' else "'" + date + "' "
        select += "ORDER BY v.creation_date desc"
        to_log('SQL Select to DB: ' + PG_DB_NAME + ' Req: ' + select[:95] + '...')
        cur.execute(select)
        rows = cur.fetchall()  # Return
        # TO LOG?: cur.rowcount
        cur.close()
    except psycopg2.Error as error:
        to_log('SQL ERROR: ' + str(error), 1)  # SQL ERROR select
    finally:
        if conn is not None:
            conn.close()
        return rows


# Запрос по task_uuid - получить результат\статус
def get_uuid_req(task_uuid, status='result'):
    if task_uuid:
        url = BASE_URL + RESULT_URL if status == 'result' else BASE_URL + STATUS_URL
        params = {"token": TOKEN, "task": task_uuid}
        resp = requests.get(url=url, json=params)
        if chk_resp(resp):
            if status == 'result':
                to_log('Result taken for Task_UUID: ' + task_uuid)
                return resp.json()['response']['result']
            else:
                to_log('Status ' + str(resp.json()['response']['status']) + ' for Task_UUID: ' + task_uuid)
                return resp.json()['response']['status']
    to_log('Task_UUID failure: ' + task_uuid, 2)
    return False  # TO LOG


# Получаем task_uuid из списка бандитов
def get_uuid(req_array):
    if len(req_array) == 0:
        to_log('Error while getting Task_UUID. Request array error', 2)
        return False  # TO LOG
    reqst = {"token": TOKEN, "request": []}

    for elem in req_array:
        typo = len(elem)
        if isinstance(elem, str):  # Поиск по ИП
            subtask_js = {"type": 3, "params": {"number": elem}}
        elif typo == 2:             # Поиск по имени и адресу - Юрики
            subtask_js = {"type": 2, "params": {"name": elem[0], "address": elem[1], "region": 77}}
        elif 3 < typo < 10:         # Поиск по ФИО+ДР
            subtask_js = {"type": 1,
                          "params": {"firstname": elem[1],
                                     "lastname": elem[0],
                                     "secondname": elem[2],
                                     "region": 77,
                                     "birthdate": elem[3]}
                          }
        else:
            to_log('Type arr error: ' + str(typo) + ' for elem ' + str(elem), 2)
            subtask_js = False
        reqst["request"].append(subtask_js)

    url = BASE_URL + GROUP_URL
    response = requests.post(url=url, json=reqst)
    if chk_resp(response):
        to_log('Get task for ' + str(len(req_array)) + ' requests. Task_UUID: ' + response.json()['response']['task'])
        return response.json()['response']['task']
    else:
        to_log('Error while getting Task_UUID', 1)
        return False


# Проверка пока не выполнится TASK
def get_uuid_finish(task_uuid):
    if task_uuid is False:
        to_log('No task to check status. Task UUID error.', 2)
        return False
    to_log('Getting result for tasks. Wait while finish! Task UUID: ' + task_uuid)
    time.sleep(PAUSE / 3)
    while True:
        status = get_uuid_req(task_uuid, 'status')
        if status is False:
            to_log('Task status error. Task_UUID: ' + task_uuid, 2)
            return False
        if status == 3:
            to_log('Task params error. Task_UUID: ' + task_uuid, 2)
            return False
        elif status == 2:
            to_log('Task not started. Task_UUID: ' + task_uuid + '. Next Request after ' + str(PAUSE) + ' seconds')
        elif status == 1:
            to_log('Task not finished. Task_UUID: ' + task_uuid + '. Next Request after ' + str(PAUSE) + ' seconds')
        elif status == 0:
            to_log('Task finished. Task_UUID: ' + task_uuid)
            return True
        time.sleep(PAUSE)


# Вывод результата
def get_uuid_result(task_uuid):
    result = []
    json_resp = get_uuid_req(task_uuid)
    if json_resp is False:
        return False
    for sub_task in json_resp:
        calc = violation_calc(sub_task)
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
    return result


# Проверка на статус ответа запроса
def chk_resp(response):
    if response.status_code != 200:  # Если ответ - ошибка
        to_log("Request error, CODE: " + str(response.status_code) + ' Exception: ' + response.json()["exception"], 1)
        return False
    js_resp = response.json()
    if js_resp['status'] != 'success':  # Если статус запроса - ошибка
        to_log("Request error, Status: " + js_resp['status'], 1)
        return False
    return True


# Убираем дубли из массива
def chk_req_arr(ar):
    to_del = []
    n = len(ar)
    for x in range(n):
        if x in to_del:
            continue
        for y in range(n):
            if x == y:
                continue
            elif y in to_del:
                continue
            else:
                if isinstance(ar[y], str):
                    if ar[x] == ar[y]:
                        to_del.append(y)
                else:
                    typo = len(ar[y])
                    if typo == 2 and ar[x][0] == ar[y][0] and ar[x][1] == ar[y][1]:
                        to_del.append(y)
                    elif 3 < typo < 10:
                        if ar[x][0] == ar[y][0] and ar[x][1] == ar[y][1] and ar[y][2] == ar[x][2] and ar[x][3] == ar[y][3]:
                            to_del.append(y)
                    else:
                        to_log('Row request type error. Count of elements: ' + str(typo), 2)  # TO LOG
                        to_del.append(y)
    to_del.sort(reverse=True)
    arc = ar[:]  # А то удаляется из глобального входящего массива
    to_log('Deleted doubles and errors from request. Count: ' + str(len(to_del)))
    for xxx in to_del:
        del arc[xxx]
    return arc


# Подготавливаем массив для выгрузки в xlsx
def xlsx_arr(request_array, result_array):
    ff = []
    counter = 0
    to_log('Requests count: ' + str(len(request_array)) + ". Beware, non SQL requests don't save in result file!!!")
    for reqst in request_array:
        for res in result_array:
            typo = len(reqst)
            if isinstance(reqst, str) and res[0] == 3:  # для номеров ип
                if reqst == res[1]:
                    to_log('IP: ' + reqst + ' payout ' + str(res[2]))
            elif typo == 2 and res[0] == 2:             # для юр лиц
                if reqst[0] == res[1]:
                    to_log('OOO: ' + reqst[0] + ' payout ' + str(res[2]))
            elif 9 > typo > 3 and res[0] == 1:          # Берем физиков но не sql
                if reqst[0] == res[1] and reqst[1] == res[2] and reqst[2] == res[3] and reqst[3] == res[4]:
                    to_log('FIZ: ' + " ".join(map(str, reqst[:3])) + ' payout ' + str(res[5]))
            elif typo == 9 and res[0] == 1:             # Берем только sql записи \ ищем среди физиков
                if reqst[0] == res[1] and reqst[1] == res[2] and reqst[2] == res[3] and reqst[3] == res[4]:
                    add = [reqst[4], reqst[5], reqst[6], reqst[7], reqst[8], '', '', res[5]]
                    to_log('SQL: ' + "; ".join(map(str, add)))
                    ff.append(add)
                    counter += 1
    to_log('Results SQL format: ' + str(counter))
    return ff


# Посчитать сумму штрафа из task['result'] JSON
def violation_calc(sub_task):
    calc = 'Error'
    if sub_task['status'] == 0:  # Task finish success
        calc = 0.0
        regular = r'\d+\.?\d{1,2}?\sруб'
        for violation in sub_task['result']:  # narushenie
            vio_str = re.findall(regular, violation['subject'])
            if vio_str:  # is None: для re.search
                calc2 = calc  # Счетчик
                for x in vio_str:  # На случай если в строке больше одной суммы
                    calc = round(calc + float(x[:-4]), 2)  # Без округления X.0000000000123
                to_log('Found: ' + violation['subject'] + ' Taken Value: ' + str(round(calc - calc2, 2)))
            else:
                to_log('Empty: ' + violation['subject'])
    if calc == 'Error':
        to_log('Subtask status error. Params: ' + ' '.join(str(v) for v in sub_task['query']['params'].values()), 2)
    return str(calc).replace('.', ',')


''' GO GO '''
# Проверка путей - like __init__
chk_paths()

# Получаем массив бандитов из БД - если не указанна дата, то за сегодня
#req_arr = sql_req_home('25.05.2019', znak='eq')
req_arr = sql_req(znak='eq')


''' 
Тут можно добавить новые запросы к req_arr:
    if task: req_arr.extend(ARRAY)

    для ИП:     ARRAY = ["65094/16/77024-ИП", "65094/16/77024-ИП"] 
    для Юр.Лиц: ARRAY = [["OOO Качан", "Ул. Кочерышка"],["OOO Выходи", "Ул. Выходная"]]
    для Физ:    ARRAY = [['СААПАПЕВ', 'ДЕНИС', 'АНДРЕЕВИЧ', '12.02.1994'],["АГИ", "РОМАН", "АШЕВИЧ", "11.02.1994"]]
'''
''' DEBUG ''''''
req_arr.append(("", "", "", ""))    # For ERROR TEST
# For double test
req_arr.append(("АГЕВ", "РОМН", "АНЕЕВИЧ", "22.02.2004", "xxx", "194", "194", "194", "194", "194", "1994", "14", "14"))
req_arr.append(("АГЕЕВ", "РОМАН", "АНДРЕЕВИЧ", "11.02.1994"))
req_arr.append(("СААПАПЕВ", "ДЕНИС", "АНДРЕЕВИЧ", "12.02.1994"))
req_arr.append(("АГЕЕВ", "РОМАН", "АНДРЕЕВИЧ", "11.02.1994"))
req_arr.append(("СААПАПЕВ", "ДЕНИС", "АНДРЕЕВИЧ", "12.02.1994"))
req_arr.append("65094/16/77024-ИП")
req_arr.append("1425628/16/77043-ИП")
req_arr.append("65094/16/77024-ИП")
req_arr.append("65094/16/77024-ИП")
'''''' DEBUG END '''

# Удаляем дубли запроса
req = chk_req_arr(req_arr)
# Из списка на проверку получаем task_uuid
task_id = get_uuid(req)
# Ждем пока TASK_UUID обработаются на сайте ФССП
if get_uuid_finish(task_id):
    # Получаем результат (тип, параметры, сумма штрафов)
    res_arr = get_uuid_result(task_id)
    # Подготовливаем массив для выгрузки в файлик
    xlsx = xlsx_arr(req_arr, res_arr)
    # Создаем файл из подготовленного массива
    write_csv(xlsx)

'''  EOF  '''