import re
import datetime
import os
import time

path = 'C:\\PS\\LOGS\\'

tmp_arr = []            # Временный массив

scan_arr = []           # Храним даты сканов - начало\конец
sql_arr = []            # Храним даты регистраций
fin_arr = []            # Финальный массив

#min_reg_time = 30      # Минимальное время на скан (CONFIG)
#err_scan_time = 100    # Возможная погрешность (CONFIG)

phase1 = 'BEGIN PHASE OPTIC'        # Начало сканирования
phase2 = 'END PHASE OPTIC'          # Конец сканирования

reg_scan = r'^\d{8} \d+:\d{2}:\d{2}'                    # Дата\Время в логе сканера
reg_sql = r'^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}$'     # Дата\Время SQL

scans_start_count = 0   # Debug
scans_end_count = 0     # Debug
rows_count = 0          # Debug
scans_counter = 0       # Debug

files = os.listdir(path)    # Список файлов в папке

# Фильтруем список файлов - только логи
print()
if files:
    print('В папке', path, 'Файлов:', len(files))
    print()
    for file_name in files:

        if file_name.find('.csv') > 0:  # Парсим только csv
            if len(sql_arr) == 0: # Если SQL массив пустой
                with open(path + file_name, "r") as file_content:
                    for str in file_content:
                        dt = re.search(reg_sql, str)
                        if dt:              # Если найдено совпадение
                            sql_arr.append(datetime.datetime.strptime(dt[0], '%Y-%m-%d %H:%M:%S'))
                print('Проверен CSV файл', file_name, ': найдено', len(sql_arr), 'регистраций')
            else:
                print('Проверен CSV файл', file_name, ': не соответсвует формату SQL выгрузки')

        elif file_name[0:8] == 'wscanner':
            with open(path + file_name, "r") as file_content:
                for str in file_content:
                    rows_count += 1  # Debug
                    if str.find(phase1) > 0 and len(tmp_arr) == 0:
                        dt = re.search(reg_scan, str)
                        scans_start_count += 1  # Debug
                        tmp_arr.append(datetime.datetime.strptime(dt[0], '%Y%m%d %H:%M:%S'))
                    elif str.find(phase2) > 0 and len(tmp_arr) == 1:
                        dt = re.search(reg_scan, str)
                        scans_end_count += 1  # Debug
                        tmp_arr.append(datetime.datetime.strptime(dt[0], '%Y%m%d %H:%M:%S'))
                    # Если обе даты в массиве tmp_arr - Тогда добавляем к массиву scan_arr и зануляем
                    if len(tmp_arr) == 2:
                        scan_arr.append(tmp_arr)
                        tmp_arr = []
            print('Проверен', file_name, ': найдено:', scans_start_count - scans_counter, 'фаз сканирований')
            scans_counter = scans_start_count
        else:
            print('Проверен', file_name, 'не соотвествует формату SQL-выгрузки или логов')
else:
    print('Нет файлов в папке:', path)

# Мини отчетик
print()
print('Регистраций SQL_ARR: ', len(sql_arr))
print('Сканов SCAN_ARR:', len(scan_arr))
print('Фаз начала сканирования:', scans_start_count)        # Debug
print('Фаз конца сканирования:', scans_end_count)           # Debug
print('Обработано строк:', rows_count)                      # Debug
time.sleep(2)


# Сортируем от малого к великому; reverse=True
scan_arr = sorted(scan_arr, key=lambda item: item[0])
sql_arr = sorted(sql_arr)

print()
print('SQL:', len(sql_arr), 'SCAN:', len(scan_arr))
print('Ищем первое совпадение')
time.sleep(2)
min_delta = 101
while 100 < min_delta or min_delta < -30:    # Погрешности запихнуть в переменные
 sql_min = min(sql_arr)
    scan_min = min(scan_arr, key=lambda item: item[0])
    min_delta = (sql_min - scan_min[0]).total_seconds()
    if len(scan_arr) == 0 or len(sql_arr) == 0:
        print('Выгрузки не сходятся')
        break                   # Если массивы не сходятся - выходим
    if min_delta < -30:         # 30 секунд погрешности
        print('Scan start', scan_min[0], '>', sql_min, 'RegTime. Delta:', min_delta)
        sql_arr.remove(sql_min)
    elif min_delta > 100:
        print('Scan start', scan_min[0], '<', sql_min, 'RegTime. Delta:', min_delta)
        scan_arr.remove(scan_min)
    else:
        print('Scan start', scan_min[0], '=', sql_min, 'RegTime. Delta:', min_delta)

print('Найдено совпадение', scan_arr[0][0], sql_arr[0])

print('Регистраций SQL_ARR: ', len(sql_arr))
print('Сканов SCAN_ARR:', len(scan_arr))

time.sleep(3)
print()

# Теперь сопоставляем остальные даты
n = len(sql_arr)
m = len(scan_arr)
for i in range(n):
    min_reg_time = 30       # Минимальное время на скан (CONFIG)
    err_scan_time = 100     # Возможная погрешность (CONFIG)
    '''
    if i == n - 1:          # Конец массива
        print('Last value, no SQL_Next')
        sql_delta = 0;
    else:
        sql_delta = (sql_arr[i+1] - sql_arr[i]).total_seconds()  # Дельта с началом сканирования
    '''
    for j in range(m):      #
        delta = abs(int((sql_arr[i] - scan_arr[j][0]).total_seconds()))
        tmp_arr.append([scan_arr[j][0], scan_arr[j][1], sql_arr[i], delta])
        #print('ADD:', scan_arr[j][0], scan_arr[j][1], 'REG', sql_arr[i], 'Delta', delta)

    row_min_delta = min(tmp_arr, key=lambda item: item[3])
    print('MIN Here:', row_min_delta[0], row_min_delta[1], 'REG', row_min_delta[2], 'Delta', row_min_delta[3])
    tmp_arr = []


# sql 2019-04-16 17:27:46 - 2019-04-12 09:17:36
# scan 2019-04-16 16:30:54 - 2019-04-14 09:58:53
