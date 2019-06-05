import time

# UNIQ ID FROM TIME
arr = ['A', 'B', 'C', 'D', 'E', 'F', 'N', 'X', 'Y', 'Z']
for i in range(5):
    time.sleep(0.0001)
    aa = str(time.time()).replace(".", "")
    xx = [arr[int(i)] for i in aa]
    res = ''.join(xx).center(17, 'Q')
    print('result :', res)
