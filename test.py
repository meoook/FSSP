import time

# UNIQ ID FROM TIME
arr = ['A', 'B', 'C', 'D', 'E', 'F', 'N', 'X', 'Y', 'Z']
for i in range(5):
    time.sleep(0.0001)
    aa = str(time.time()).replace(".", "")
    xx = [arr[int(i)] for i in aa]
    res = ''.join(xx).center(17, 'Q')
    print('result :', res)



class bcolors:
    C_A = '\33[95m'
    C_BLUE = '\33[94m'
    C_RED = '\33[103m'
    C_GREEN = '\33[92m'
    C_FAIL = '\33[91m'
    C_END = '\33[0m'
    C_BOLD = '\33[1m'
    C_UNDERLINE = '\33[4m'


print(bcolors.C_A + 'PINK'
      + bcolors.C_BLUE + 'BLUE'
      + bcolors.C_RED + 'YELLOW'
      + bcolors.C_GREEN + 'DGREEN'
      + bcolors.C_FAIL + 'RED'
      + bcolors.C_UNDERLINE + 'Underline'
      + bcolors.C_END + 'END'
      )


print('\x1b[30m' + '30 white' + '\x1b[0m')
print('\x1b[31m' + '31 red' + '\x1b[0m')
print('\x1b[91m' + '91 red' + '\x1b[0m')
print('\x1b[32m' + '32 green' + '\x1b[0m')
print('\x1b[93m' + '93' + '\x1b[0m')
print('\x1b[33m' + '33 orange' + '\x1b[0m')
print('\x1b[34m' + '34 blue' + '\x1b[0m')
print('\x1b[35m' + '35 pink' + '\x1b[0m')
print('\x1b[36m' + '36 water' + '\x1b[0m')
print('\x1b[37m' + '37 d_gray' + '\x1b[0m')
print('\x1b[38m' + '38 l_gray' + '\x1b[0m')
print('\x1b[39m' + '39stsdasdasd!' + '\x1b[0m')
print('\x1b[39;41m' + '40stsdasdasd!' + '\x1b[0m')
print('\x1b[30;41m' + '41stsdasdasd!' + '\x1b[0m')
print('\x1b[30;42m' + '42stsdasdasd!' + '\x1b[0m')
print('\x1b[30;43m' + 'testsdasdasd!' + '\x1b[0m')
print('\x1b[44m' + 'testsdasdasd!' + '\x1b[0m')
print('\x1b[45m' + 'testsdasdasd!' + '\x1b[0m')
print('\x1b[46m' + 'testsdasdasd!' + '\x1b[0m')
print('\x1b[47m' + 'testsdasdasd!' + '\x1b[0m')
print('\x1b[48m' + 'testsdasdasd!' + '\x1b[0m')


print('\x1b[90m' + '90 black' + '\x1b[0m')
