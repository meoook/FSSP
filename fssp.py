import requests
import time
import re
from my_colors import Color


class FSSP:
    """
    NEXT VERSION: ADD TOKEN CHECKER
    NEXT VERSION: ADD THREADING
    для Физ:    ARRAY = [['СААПАПЕВ', 'ДЕНИС', 'АНДРЕЕВИЧ', '12.02.1994'],["АГИ", "РОМАН", "АШЕВИЧ", "11.02.1994"]]
    для Юр.Лиц: ARRAY = [["OOO Качан", "Ул. Кочерышка"],["OOO Выходи", "Ул. Выходная"]]
    для ИП:     ARRAY = ["65094/16/77024-ИП", "65094/16/77024-ИП"]
    """
    def __init__(self, token='k51UxJdRmtyZ', pause=15, url='https://api-ip.fssprus.ru/api/v1.0/', log_handler=None):
        super().__init__()
        self.token = token
        self.url = url
        self.pause = int(pause) if int(pause) < 5 else 5  # Minimum value for pause
        self.region = 77    # Default - Moscow
        self.__result = []
        # Прикручиваем LOGGER
        if log_handler is None:
            def log_pass(*args, **kwargs):
                print('\33[91mFSSP class ERROR: Log handler not found. \33[93mMSG:\33[0m', args[0].format(*args[2:]))
            self.__to_log = log_pass
        else:
            self.__to_log = log_handler

    @staticmethod
    def __arr_check_doubles(arr):
        """ Убираем дубли из массива """
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
        arr_copy = arr[:]  # А то удаляется из глобального входящего массива
        to_del.sort(reverse=True)
        for double in to_del:
            del arr_copy[double]
        return arr_copy, len(to_del)

    @property
    def arr(self):
        return self.__result

    @arr.setter
    def arr(self, array):
        """ Проверяем входящий массив и сразу запускаем проверку на штрафы """
        if isinstance(array, list):
            self.__result = []
            arr, doubles_count = self.__arr_check_doubles(array)
            if doubles_count > 0:
                self.__to_log('Deleted doubles and errors from request. Count: {}', 3, doubles_count)
            if self.__uuid_get(arr):
                if self.__uuid_wait_finish():
                    self.__uuid_result()
        else:
            self.__to_log('Input type not valid: {}. Use "List" instead.', 2, type(array))

    def __request_fssp(self, url, json):
        """ Проверка на статус ответа запроса """
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
        if response.status_code != 200:  # Если ответ - ошибка
            self.__to_log("Request error, CODE: {} Exception: {}", 1, response.status_code, js_resp["exception"],
                          c1=Color.inf, c2=Color.err)
            return False
        if js_resp['status'] != 'success':  # Если статус запроса - ошибка
            self.__to_log("Request error, Status: {} ", 2, js_resp['status'])
            return False
        return response

    # Получаем UUID из списка бандитов
    def __uuid_get(self, array):
        if len(array) > 0:
            self.__to_log('Getting UUID for {} users...', 3, len(array))
        else:
            self.__to_log('Empty user list to get UUID', 2)
            return False
        reqst = {"token": self.token, "request": []}
        for elem in array:
            typo = len(elem)
            if isinstance(elem, str):  # Поиск по ИП
                self.__to_log('Add to request: {}', 3, elem)
                subtask_js = {"type": 3, "params": {"number": elem}}
            elif typo == 2:  # Поиск по имени и адресу - Юрики
                self.__to_log('Add to request: {} from {}', 3, *elem)
                subtask_js = {"type": 2, "params": {"name": elem[0], "address": elem[1], "region": self.region}}
            elif 3 < typo < 10:  # Поиск по ФИО+ДР
                self.__to_log('Add to request: {} {} {} {}', 3, *elem[0:4])
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
        """ Запрос по UUID - получить результат/статус """
        status_arr = ('Finished', 'Not finished', 'Not started', 'Result error', 'Unknown error')
        if self.__uuid:
            url = self.url + 'result' if request_for == 'result' else self.url + 'status'
            params = {"token": self.token, "task": self.__uuid}
            response = self.__request_fssp(url, params)
            if response:
                js_resp = response.json()['response']
                if request_for == 'result':
                    return js_resp['result']  # When task finished - return json array with results
                else:
                    self.__to_log('For UUID {} Requests done {} Status: {}', 3, self.__uuid,
                                  js_resp['progress'], status_arr[js_resp['status']])
                    return js_resp['status']
        self.__to_log('UUID {} failure', 2, self.__uuid)
        return False

    def __uuid_wait_finish(self):
        """ Проверка пока не выполнится TASK или какая ошибка """
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
        """ Получив пложительный результат о выполнении taks выводим массив с результами. """
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
        """ Посчитать сумму штрафа из task['result'] JSON """
        calc = 0.0
        regular = r'\d+\.?\d{1,2}?\sруб'
        if sub_task['status'] == 0:     # Task finish success
            for violation in sub_task['result']:  # narushenie
                vio_str = re.findall(regular, violation['subject'])
                if vio_str:             # is None: для re.search
                    for x in vio_str:   # На случай если в строке больше одной суммы
                        calc = round(calc + float(x[:-4]), 2)  # Без округления X.0000000000123
        return calc    # str(calc).replace('.', ',')


if __name__ == '__main__':

    req_arr = [("", "", "", ""),
               ("АГЕВ", "РОМН", "АНЕЕВИЧ", "22.02.2004", "xxx", "194", "194", "194", "194", "194", "1994", "14", "14"),
               ("АГЕЕВ", "РОМАН", "АНДРЕЕВИЧ", "11.02.1994"), ("СААПАПЕВ", "ДЕНИС", "АНДРЕЕВИЧ", "12.02.1994"),
               ("АГЕЕВ", "РОМАН", "АНДРЕЕВИЧ", "11.02.1994"), ("СААПАПЕВ", "ДЕНИС", "АНДРЕЕВИЧ", "12.02.1994"),
               "65094/16/77024-ИП", "1425628/16/77043-ИП", "65094/16/77024-ИП", "65094/16/77024-ИП"]

    app = FSSP('k51UxJdRmtyZ')
    #app.arr = req_arr
    app.arr = "hgjgjhgjgjmghjh"
    print(app.arr)

