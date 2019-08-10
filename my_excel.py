from datetime import datetime
import xlsxwriter
import time

# Create a workbook and add a worksheet.
workbook = xlsxwriter.Workbook('test.xlsx')
worksheet = workbook.add_worksheet()

# Add a bold format to use to highlight cells.
header = workbook.add_format({'font_size': 11, 'bold': 1, 'bg_color': '#FED0C0'})

# Add a number format for cells with money.
money_format = workbook.add_format({'num_format': '# ##0.00" ₽"'})

# Add an Excel date format.
date_format = workbook.add_format({'num_format': 'dd.mm.yyyy h:mm'})

# Adjust the column width.
worksheet.set_column('A:A', 16)  # Set format for col 1.

# Write some data headers.
worksheet.write('A1', 'ДАТА', header)
worksheet.write('B1', 'АДРЕС', header)
worksheet.write('C1', 'Участок', header)
worksheet.write('D1', 'РЕЕСТР', header)
worksheet.write('E1', 'Контрольная Сумма', header)
worksheet.write('F1', 'Комментарий', header)
worksheet.write('G1', 'Задержаний', header)
worksheet.write('H1', 'Сумма взысканий', header)

# Some data we want to write to the worksheet.
test_data = (
 ['05.08.2019 12:28', 'г. Москва, ул. Красного Маяка, д. 13-б', 230, 'ФССП', 'd421166fd142e331b0d8df3fe059d2f1',
  'Сообщили в ФССП. Снят с базы.', '', '46352.13'],
 ['02.08.2019 10:08',  'г. Москва, пр-д Одоевского, д. 11, корп. 7',  62, 'ФССП', '3c20f2fe7dd784395ca0960e6a95db65',
  'Сообщили приставу', 'ЗАДЕРЖАН', '85000.00'],
 ['02.08.2019 9:54', 'г. Москва, ул. Игральная, д. 5, корп. 1',  108, 'ФССП', 'd4541a5af79fe38ef8d61df9f2b8e6b6',
  'Сообщили в ФССП. Снят с базы.', '', '24015.00'],
 ['01.08.2019 17:47',  'г. Москва, ул. Кубанская, д. 23',   249, 'ФССП', '629b9f830a9ae0d2b7ec8d07b469babe',
  'Сообщили приставу', '', '274124.86'],
 ['01.08.2019 15:49',  'г. Москва, ул. Верейская, д. 21',   196, 'МВД', 'fe1650ebe436af099e103c0337633094',
  'Сообщили приставу', '', '106000.00'],
)

# Start from the first cell below the headers.
row = 2
for date, adr, court, reg, c_sum, comm, jail, pay_sum in test_data:
    # Convert the date string into a datetime object.
    date1 = datetime.strptime(date, "%d.%m.%Y %H:%M")

    worksheet.write_datetime(row, 0, date1, date_format)
    worksheet.write_string(row, 1, adr)
    worksheet.write_number(row, 2, int(court))
    worksheet.write_string(row, 3, reg)
    worksheet.write_string(row, 4, c_sum)
    worksheet.write_string(row, 5, comm)
    worksheet.write_string(row, 6, jail)
    worksheet.write_number(row, 7, float(pay_sum), money_format)
    row += 1

# Write a total using a formula.
worksheet.write(1, 0, 'Total', header)
worksheet.write(1, 7, '=SUM(H3:H25)', money_format)

workbook.close()