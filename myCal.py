import calendar
'''
import locale
locale.setlocale(locale.LC_ALL, 'ru_RU')
print(calendar.month_name[1])
'''

cal = calendar.TextCalendar(firstweekday=0)

print(cal.formatmonth(2019, 6, w=0, l=0))


# print(calendar.weekday(2019, 7, 8))   # Returns day of the week

# GOOD - all values in month + nearest
#for a in cal.itermonthdays4(2019, 6):
#    print(a)

# DATE TIME RETURN (week like rows)
#for c in objCal.monthdatescalendar(2019, 6):
#    print(c)


''' Разбор на строки и вывод
kk = calendar.month(2019, 6)
arr = kk.split('\n')

for row in arr:
    print(row)
'''
