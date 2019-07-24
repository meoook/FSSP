import requests
import time
import re


class FSSP:
    """
    NEXT VERSION: ADD THREADING
    для Физ:    ARRAY = [['СААПАПЕВ', 'ДЕНИС', 'АНДРЕЕВИЧ', '12.02.1994'],["АГИ", "РОМАН", "АШЕВИЧ", "11.02.1994"]]
    для Юр.Лиц: ARRAY = [["OOO Качан", "Ул. Кочерышка"],["OOO Выходи", "Ул. Выходная"]]
    для ИП:     ARRAY = ["65094/16/77024-ИП", "65094/16/77024-ИП"]
    """
    def __init__(self, token='k51UxJdRmtyZ', pause=15, url='https://api-ip.fssprus.ru/api/v1.0/'):
        super().__init__()
        self.token = token
        self.url = url
        self.pause = pause
        self.__result = False

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
        to_del.sort(reverse=True)
        arr_copy = arr[:]  # А то удаляется из глобального входящего массива
        for double in to_del:
            del arr_copy[double]
        return arr_copy

    @property
    def arr(self):
        return self.__result

    @arr.setter
    def arr(self, array):
        self.__result = False
        arr = self.__arr_check_doubles(array)
        if self.__uuid_get(arr):
            if self.__uuid_wait_finish():
                self.__uuid_result()

    @staticmethod
    def __response_status(response):
        """ Проверка на статус ответа запроса """
        if response.status_code != 200:  # Если ответ - ошибка
            return False
        if response.json()['status'] != 'success':  # Если статус запроса - ошибка
            return False
        return True

    # Получаем TASK_UUID из списка бандитов
    def __uuid_get(self, array):
        reqst = {"token": self.token, "request": []}
        for elem in array:
            typo = len(elem)
            if isinstance(elem, str):  # Поиск по ИП
                subtask_js = {"type": 3, "params": {"number": elem}}
            elif typo == 2:  # Поиск по имени и адресу - Юрики
                subtask_js = {"type": 2, "params": {"name": elem[0], "address": elem[1], "region": 77}}
            elif 3 < typo < 10:  # Поиск по ФИО+ДР
                subtask_js = {"type": 1,
                              "params": {"firstname": elem[1],
                                         "lastname": elem[0],
                                         "secondname": elem[2],
                                         "region": 77,
                                         "birthdate": elem[3]}
                              }
            else:
                subtask_js = False
            reqst["request"].append(subtask_js)

        url = self.url + 'search/group'
        response = requests.post(url=url, json=reqst)
        print('UUID GETTING')
        if self.__response_status(response):
            self.__uuid = response.json()['response']['task']
            return True
        else:
            return False    # Error getting UUID

    def __uuid_req(self, request_for='result'):
        """ Запрос по TASK_UUID - получить результат/статус """
        if self.__uuid:
            url = self.url + 'result' if request_for == 'result' else self.url + 'status'
            params = {"token": self.token, "task": self.__uuid}
            resp = requests.get(url=url, json=params)
            if self.__response_status(resp):
                if request_for == 'result':
                    return resp.json()['response']['result']  # When task finished - return json array
                else:
                    return resp.json()['response']['status']  # ['Success', 'Not finished', 'Not started', 'Error3', 'Error4']
        return False

    def __uuid_wait_finish(self):
        """ Проверка пока не выполнится TASK или какая ошибка """
        while True:
            status = self.__uuid_req('status')
            print('WAIT WHILE FINISH', status)
            if status is False or status == 3:
                return False
            elif status == 0:
                return True
            elif status in (1, 2):
                time.sleep(int(self.pause))

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
        return True

    @staticmethod
    def __violation_calc(sub_task):
        # Посчитать сумму штрафа из task['result'] JSON
        calc = 0.0
        regular = r'\d+\.?\d{1,2}?\sруб'
        if sub_task['status'] == 0:  # Task finish success
            for violation in sub_task['result']:  # narushenie
                vio_str = re.findall(regular, violation['subject'])
                if vio_str:  # is None: для re.search
                    for x in vio_str:  # На случай если в строке больше одной суммы
                        calc = round(calc + float(x[:-4]), 2)  # Без округления X.0000000000123
        return str(calc).replace('.', ',')


if __name__ == '__main__':

    req_arr = [("", "", "", ""),
               ("АГЕВ", "РОМН", "АНЕЕВИЧ", "22.02.2004", "xxx", "194", "194", "194", "194", "194", "1994", "14", "14"),
               ("АГЕЕВ", "РОМАН", "АНДРЕЕВИЧ", "11.02.1994"), ("СААПАПЕВ", "ДЕНИС", "АНДРЕЕВИЧ", "12.02.1994"),
               ("АГЕЕВ", "РОМАН", "АНДРЕЕВИЧ", "11.02.1994"), ("СААПАПЕВ", "ДЕНИС", "АНДРЕЕВИЧ", "12.02.1994"),
               "65094/16/77024-ИП", "1425628/16/77043-ИП", "65094/16/77024-ИП", "65094/16/77024-ИП"]

    app = FSSP('k51UxJdRmtyZ')
    app.arr = req_arr
    print(app.arr)

