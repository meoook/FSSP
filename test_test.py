START = [['1', '2', '3', '4', '5', '9'], ['2', '11'], ['7', '8'], ['45', '92'], ['6', '11'], ['92', '0']]

FINAL = []

n = len(START)
to_del = []

def check:




for x in range(n):
    for elem in START[x]:
        if x + 1 < n:
            for z in range(x+1, n):
                print(elem, START[z])
                if elem in START[z]:
                    print('found', elem, 'in', START[z])
                    [tmp.append(y) for y in START[x]]
                    [tmp.append(y) for y in START[z]]
                    FINAL.append(tmp)
                    to_del.append(x)
                    vvv = True

for x in to_del:
    del START[x]

FINAL += START

print(FINAL)
