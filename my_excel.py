from datetime import datetime
import xlsxwriter

# Create a workbook and add a worksheet.
workbook = xlsxwriter.Workbook('test.xlsx')
worksheet = workbook.add_worksheet()

# Add headers formats
fmt_h1 = workbook.add_format({'bold': 1, 'bg_color': '#FEE0D0', 'align': 'center', 'valign': 'vcenter', 'border': 1})
fmt_h2 = workbook.add_format({'bold': 1, 'bg_color': '#77BBF0', 'align': 'center', 'valign': 'vcenter', 'border': 1})
fmt_h2_money = workbook.add_format({'num_format': '# ##0.00" ₽"', 'font_size': 11, 'bold': 1, 'bg_color': '#77BBF0', 'align': 'right', 'valign': 'vcenter', 'border': 1})
# Table formats
fmt_date = workbook.add_format({'num_format': 'dd.mm.yyyy h:mm', 'border': 1})
fmt_adr = workbook.add_format({'indent': 1, 'border': 1})
fmt_center = workbook.add_format({'align': 'center', 'border': 1})
fmt_money = workbook.add_format({'num_format': '# ##0.00" ₽"', 'border': 1})
fmt_bd = workbook.add_format({'border': 1})
# HighLight formats
fmt_hl_red = workbook.add_format({'bg_color': '#FFCCCC', 'font_color': '#FF0000'})
fmt_hl_green = workbook.add_format({'bg_color': '#CCFFCC', 'font_color': '#007700'})

# Adjust the column width.
worksheet.set_column('A:A', 16)     # Date
worksheet.set_column('B:B', 47)     # Address
worksheet.set_column('C:C', 7.3)    # Court
worksheet.set_column('D:D', 18)     # Registry
worksheet.set_column('E:E', 36)     # C_SUM
worksheet.set_column('F:F', 58)     # Comment
worksheet.set_column('G:G', 11.3)   # Jail
worksheet.set_column('H:H', 17)     # PaySum
# Adjust the row height.
worksheet.set_row(0, 25)
worksheet.set_row(1, 25)
# Header
worksheet.write('A1', 'ДАТА', fmt_h1)
worksheet.write('B1', 'АДРЕС', fmt_h1)
worksheet.write('C1', 'Участок', fmt_h1)
worksheet.write('D1', 'РЕЕСТР', fmt_h1)
worksheet.write('E1', 'Контрольная Сумма', fmt_h1)
worksheet.write('F1', 'Комментарий', fmt_h1)
worksheet.write('G1', 'Задержаний', fmt_h1)
worksheet.write('H1', 'Сумма взысканий', fmt_h1)
# Header count
worksheet.write(1, 0, 'ИТОГО', fmt_h2)
worksheet.write(1, 1, '=CONCATENATE("Нарушителей: ", COUNT(C:C))', fmt_h2)
worksheet.write(1, 2, '', fmt_h2)
worksheet.write(1, 3, '=CONCATENATE("ФССП: ", COUNTIF(D3:D1125,"ФССП"), " МВД: ", COUNTIF(D3:D1125,"МВД"))', fmt_h2)
worksheet.write(1, 4, '', fmt_h2)
worksheet.write(1, 5, '', fmt_h2)
worksheet.write(1, 6, '=COUNTIF(G3:G1125, "ЗАДЕРЖАН")', fmt_h2)
worksheet.write(1, 7, '=SUM(IF(FREQUENCY(MATCH(E3:E8, E3:E8, 0), MATCH(E3:E8, E3:E8, 0))>0, H3:H8, 0))', fmt_h2_money)
# Conditional formatting
worksheet.conditional_format('D3:D100', {'type':     'cell',
                                         'criteria': '==',
                                         'value':    '"МВД"',
                                         'format':   fmt_hl_red})
worksheet.conditional_format('D3:D100', {'type':     'cell',
                                         'criteria': '==',
                                         'value':    '"ФССП"',
                                         'format':   fmt_hl_green})
worksheet.conditional_format('E3:E100', {'type':     'formula',
                                         'criteria': '=COUNTIF($E$3:$E$10000, E3)>1',
                                         'format':   fmt_hl_red})
worksheet.conditional_format('G3:G100', {'type':     'cell',
                                         'criteria': '==',
                                         'value':    '"ЗАДЕРЖАН"',
                                         'format':   fmt_hl_red})

# Some data we want to write to the worksheet.
test_data = (
 ['05.08.2019 12:28:22', 'г. Москва, ул. Красного Маяка, д. 13-б', 230, 'ФССП', 'd421166fd142e331b0d8df3fe059d2f1',
  'Сообщили в ФССП. Снят с базы.', '', '46352.13'],
 ['05.08.2019 14:38:11', 'г. Москва, ул. Красного Маяка, д. 13-б', 230, 'ФССП', 'd421166fd142e331b0d8df3fe059d2f1',
  'Сообщили в ФССП. Снят с базы.', '', '46352.13'],
 ['02.08.2019 10:08:34',  'г. Москва, пр-д Одоевского, д. 11, корп. 7',  62, 'ФССП', '3c20f2fe7dd784395ca0960e6a95db65',
  'Сообщили приставу', 'ЗАДЕРЖАН', '85000.00'],
 ['02.08.2019 9:54:41', 'г. Москва, ул. Игральная, д. 5, корп. 1',  108, 'ФССП', 'd4541a5af79fe38ef8d61df9f2b8e6b6',
  'Сообщили в ФССП. Снят с базы.', '', '24015.00'],
 ['01.08.2019 17:47:02',  'г. Москва, ул. Кубанская, д. 23',   249, 'ФССП', '629b9f830a9ae0d2b7ec8d07b469babe',
  'Сообщили приставу', '', '274124.86'],
 ['01.08.2019 15:49:12',  'г. Москва, ул. Верейская, д. 21',   196, 'МВД', 'fe1650ebe436af099e103c0337633094',
  'Сообщили приставу', '', '106000.00'],
)

# Start from the first cell below the headers.
row = 2

for date, adr, court, reg, c_sum, comm, jail, pay_sum in test_data:
    # Convert the date string into a datetime object.
    date1 = datetime.strptime(date, "%d.%m.%Y %H:%M:%S")

    worksheet.write_datetime(row, 0, date1, fmt_date)
    worksheet.write_string(row, 1, adr, fmt_adr)
    worksheet.write_number(row, 2, int(court), fmt_center)
    worksheet.write_string(row, 3, reg, fmt_center)
    worksheet.write_string(row, 4, c_sum, fmt_bd)
    worksheet.write_string(row, 5, comm, fmt_bd)
    worksheet.write_string(row, 6, jail, fmt_center)
    worksheet.write_number(row, 7, float(pay_sum), fmt_money)
    row += 1


workbook.close()