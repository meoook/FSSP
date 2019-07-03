import time

# UNIQ ID FROM TIME
arr = ['A', 'B', 'C', 'D', 'E', 'F', 'N', 'X', 'Y', 'Z']
for i in range(5):
    time.sleep(0.0001)
    aa = str(time.time()).replace(".", "")
    xx = [arr[int(i)] for i in aa]
    res = ''.join(xx).center(17, 'Q')
    print('result :', res)




class frmt:
    C_A = '\33[95m'
    C_BLUE = '\33[94m'
    C_RED = '\33[103m'
    C_GREEN = '\33[92m'
    C_FAIL = '\33[91m'
    C_END = '\33[0m'
    C_BOLD = '\33[1m'
    C_UNDERLINE = '\33[4m'


print('----- MAIN COLOR -----')
print('\x1b[30m' + '30 white' + '\x1b[0m')
print('\x1b[38m' + '38 l_gray' + '\x1b[0m')
print('\x1b[37m' + '37 gray' + '\x1b[0m')
print('\x1b[90m' + '90 d_gray' + '\x1b[0m')
print('\x1b[97m' + '97 black' + '\x1b[0m')
print('\x1b[31m' + '31 d_red' + '\x1b[0m')
print('\x1b[91m' + '91 l_red' + '\x1b[0m')
print('\x1b[32m' + '32 green' + '\x1b[0m')
print('\x1b[92m' + '92 green' + '\x1b[0m')
print('\x1b[33m' + '33 orange' + '\x1b[0m')
print('\x1b[93m' + '93 yellow' + '\x1b[0m')
print('\x1b[34m' + '34 blue' + '\x1b[0m')
print('\x1b[94m' + '94 l_blue' + '\x1b[0m')
print('\x1b[35m' + '35 purple' + '\x1b[0m')
print('\x1b[95m' + '95 pink' + '\x1b[0m')
print('\x1b[36m' + '36 water' + '\x1b[0m')
print('\x1b[96m' + '96 sky' + '\x1b[0m')
print('----- BACKGROUND -----')
print('\x1b[40m' + '40 white' + '\x1b[0m')
print('\x1b[47m' + '47 l_gray' + '\x1b[0m')
print('\x1b[100m' + '100 d_gray' + '\x1b[0m')
print('\x1b[107m' + '107 black' + '\x1b[0m')
print('\x1b[41m' + '41 d_red' + '\x1b[0m')
print('\x1b[101m' + '101 l_red' + '\x1b[0m')
print('\x1b[42m' + '42 green' + '\x1b[0m')
print('\x1b[102m' + '102 green' + '\x1b[0m')
print('\x1b[43m' + '43 orange' + '\x1b[0m')
print('\x1b[103m' + '103 yellow' + '\x1b[0m')
print('\x1b[44m' + '44 blue' + '\x1b[0m')
print('\x1b[104m' + '104 l_blue' + '\x1b[0m')
print('\x1b[45m' + '45 purple' + '\x1b[0m')
print('\x1b[105m' + '105 pink' + '\x1b[0m')
print('\x1b[46m' + '46 water' + '\x1b[0m')
print('\x1b[106m' + '106 sky' + '\x1b[0m')
print('----- EXAMPLE -----')
print('\x1b[1;97;40m' + '1;97;40 1=BOLD' + '\x1b[0m')
print('\x1b[97;47m' + '97;47' + '\x1b[0m')
print('\x1b[4;32;100m' + '4;32;100 4=Underline' + '\x1b[0m')
print('\x1b[30;107m' + '30;107' + '\x1b[0m')

