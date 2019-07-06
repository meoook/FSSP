
def anton(x,y):
    print(x*y)

def sanek(x, y):
    for xa in range(x):
        anton(xa,y)

x = 50
y = 12

sanek(x,y)