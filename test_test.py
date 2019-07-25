def rm_double(arr):
    result = []
    for value in arr:
        if value not in result:
            result.append(value)
    result.sort(key=lambda v: int(v))   # Хочешь еще сортировку
    return result


START = [['1', '2', '3', '4', '5', '9'], ['3', '11'], ['2', '11'], ['7', '8'], ['45', '92'], ['6', '11'], ['92', '0']]
print('START', START)

FINAL = [START[0]]
START = START[1:]

# Смысл примерно такой - есть финальный массив. Если значение в его строке есть в начальном массиве, тогда
# дописивыем к !строке финального!, а если нет - то дописываем к !финальному массиву!
while len(START) != 0:
    for M, f_row in enumerate(FINAL):
        not_found = True
        for val in f_row:
            for s_row in START:
                #print('Looking fo val {} in s_row: {}'.format(val, s_row))
                if val in s_row:
                    [FINAL[M].append(x) for x in s_row]
                    START.remove(s_row)
                    #print('FOUND S', START)
                    #print('FOUND F', FINAL)
                    not_found = False
                    break
        if not_found:
            FINAL.append(START[0])
            START.remove(START[0])
            #print('NOT FOUND S', START)
            #print('NOT FOUND F', FINAL)

print('FINAL', FINAL)
FINAL = [rm_double(x) for x in FINAL]
print('FINAL INT, SORTED, REMOVE DOUBLES', FINAL)

