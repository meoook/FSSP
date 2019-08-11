from datetime import datetime
import xlsxwriter
from my_database import DbLocal


class Excel:
    """ To save FSSP data in excel format. """
    def __init__(self, f_name='test.xlsx', log_handler=None):
        self.f_name = f_name
        self.__fmt_h_def = {'bold': 1, 'align': 'center', 'valign': 'vcenter', 'border': 1}
        # Прикручиваем LOGGER
        if log_handler is None:
            def log_pass(*args, **kwargs):
                print('\33[91mExcel class ERROR: Log handler not found. \33[93mMSG:\33[0m', args[0].format(*args[2:]))
            self._to_log = log_pass
        else:
            self._to_log = log_handler
        # Create a workbook and add a worksheet.
        if self.__workbook_can_create():
            self.__workbook = xlsxwriter.Workbook(self.f_name)
            self._to_log('WorkBook {} created.', 3, self.f_name)

    def data_from_db(self, conditions=None):
        db = DbLocal('fssp', self._to_log)
        db.table = conditions if conditions and isinstance(conditions, dict) else {'uniq': False}
        self.data(db.table)
        if not conditions:
            db.table = {'uniq': True}
            self.data(db.table, 'ruk')
        self.__workbook.close()

    def data(self, array, sheet='main'):
        if isinstance(array, list) and len(array) > 0:
            if self.__workbook_can_create():
                # PaySum format
                fmt_tmp = {'bold': 1, 'align': 'right', 'valign': 'vcenter', 'border': 1, 'bg_color': '#77BBF0'}
                fmt_h2_money = self.__workbook.add_format({'num_format': "# ### ### ##0.00 ₽", **fmt_tmp})
                # HighLight formats
                fmt_hl_red = self.__workbook.add_format({'bg_color': '#FFCCCC', 'font_color': '#FF0000'})
                fmt_hl_green = self.__workbook.add_format({'bg_color': '#CCFFCC', 'font_color': '#005500'})
                fmt_hl_yellow = self.__workbook.add_format({'bg_color': '#FFFF00'})
                # Table formats
                fmt_h2 = self.__workbook.add_format({'bg_color': '#77BBF0', **self.__fmt_h_def})
                fmt_date = self.__workbook.add_format({'num_format': 'dd.mm.yyyy h:mm', 'border': 1, 'align': 'left', 'indent': 1})
                fmt_adr = self.__workbook.add_format({'indent': 1, 'border': 1})
                fmt_center = self.__workbook.add_format({'align': 'center', 'border': 1})
                fmt_money = self.__workbook.add_format({'num_format': '# ### ### ##0.00 ₽', 'border': 1})
                fmt_bd = self.__workbook.add_format({'border': 1})

                def add_row(idx, data):
                    date, adr, court, reg, c_sum, comm, jail, pay_sum = data
                    # Convert the date string into a datetime object.
                    date = datetime.strptime(date, "%d.%m.%Y %H:%M:%S")
                    comm = '' if not comm or comm == 'None' else comm
                    jail = '' if not jail or jail == 'None' or (sheet == 'ruk' and reg == 'ФССП') else jail
                    pay_sum = float(pay_sum) if pay_sum else 0
                    if sheet == 'main':
                        self.__main_p.write_datetime(idx, 0, date, fmt_date)
                        self.__main_p.write_string(idx, 1, adr, fmt_adr)
                        self.__main_p.write_number(idx, 2, int(court), fmt_center)
                        self.__main_p.write_string(idx, 3, reg, fmt_center)
                        self.__main_p.write_string(idx, 4, c_sum, fmt_bd)
                        self.__main_p.write_string(idx, 5, comm, fmt_bd)
                        self.__main_p.write_string(idx, 6, jail, fmt_center)
                        self.__main_p.write_number(idx, 7, pay_sum, fmt_money)
                    elif sheet == 'ruk':
                        self.__ruk_p.write_datetime(idx, 0, date, fmt_date)
                        self.__ruk_p.write_string(idx, 1, adr, fmt_adr)
                        self.__ruk_p.write_number(idx, 2, int(court), fmt_center)
                        self.__ruk_p.write_string(idx, 3, reg, fmt_center)
                        self.__ruk_p.write_string(idx, 4, comm, fmt_bd)
                        self.__ruk_p.write_string(idx, 5, jail, fmt_center)
                        self.__ruk_p.write_number(idx, 6, pay_sum, fmt_money)

                self.__sheet_create(sheet)
                if sheet == 'main':
                    obj = self.__main_p
                    row_idx = 2
                    # Conditional formatting
                    obj.conditional_format('D3:D10000', {'type': 'cell',
                                                         'criteria': '==',
                                                         'value': '"МВД"',
                                                         'format': fmt_hl_red})
                    obj.conditional_format('D3:D10000', {'type': 'cell',
                                                         'criteria': '==',
                                                         'value': '"ФССП"',
                                                         'format': fmt_hl_green})
                    obj.conditional_format('E3:E10000', {'type': 'formula',
                                                         'criteria': '=COUNTIF($E$3:$E$10000, E3)>1',
                                                         'format': fmt_hl_red})
                    obj.conditional_format('G3:G10000', {'type': 'cell',
                                                         'criteria': '==',
                                                         'value': '"ЗАДЕРЖАН"',
                                                         'format': fmt_hl_red})
                    obj.conditional_format('H3:H10000', {'type': 'formula',
                                                         'criteria': '=COUNTIF($E$3:$E$10000, E3)>1',
                                                         'format': fmt_hl_yellow})
                else:
                    obj = self.__ruk_p
                    row_idx = 4
                    # Conditional formatting
                    obj.conditional_format('D5:D10000', {'type': 'cell',
                                                                   'criteria': '==',
                                                                   'value': '"МВД"',
                                                                   'format': fmt_hl_red})
                    obj.conditional_format('D5:D10000', {'type': 'cell',
                                                               'criteria': '==',
                                                               'value': '"ФССП"',
                                                               'format': fmt_hl_green})
                    obj.conditional_format('F5:F10000', {'type': 'cell',
                                                         'criteria': '==',
                                                         'value': '"ЗАДЕРЖАН"',
                                                         'format': fmt_hl_red})

                # Start from the first cell below the headers.
                for row_add in array:
                    if len(row_add) == 8:
                        add_row(row_idx, row_add)
                        row_idx += 1
                    elif len(row_add) == 12:
                        add_row(row_idx, row_add[4:])
                        row_idx += 1
                    else:
                        self._to_log('Error adding row: {}', 2, row_add)

                # Add Header count
                if sheet == 'main':
                    obj.write(1, 0, 'ИТОГО', fmt_h2)
                    obj.write(1, 1, '=CONCATENATE("Нарушителей: ", COUNT(C:C))', fmt_h2)
                    obj.write(1, 2, '', fmt_h2)
                    obj.write(1, 3, '=CONCATENATE("ФССП: ",COUNTIF(D3:D10000,"ФССП")," МВД: ",COUNTIF(D3:D10000,"МВД"))', fmt_h2)
                    obj.write(1, 4, '', fmt_h2)
                    obj.write(1, 5, '', fmt_h2)
                    obj.write(1, 6, '=COUNTIF(G3:G10000, "ЗАДЕРЖАН")', fmt_h2)
                    obj.write(1, 7, f'=SUM(IF(FREQUENCY(MATCH(E3:E{row_idx}, E3:E{row_idx}, 0),'
                                        f'MATCH(E3:E{row_idx}, E3:E{row_idx}, 0))>0, H3:H{row_idx}, 0))', fmt_h2_money)
                else:
                    obj.write(3, 0, 'ИТОГО', fmt_h2)
                    obj.write(3, 1, '=CONCATENATE("Нарушителей: ", COUNT(C:C))', fmt_h2)
                    obj.write(3, 2, '', fmt_h2)
                    obj.write(3, 3, '=CONCATENATE("ФССП: ",COUNTIF(D5:D10000,"ФССП")," МВД: ",COUNTIF(D5:D10000,"МВД"))', fmt_h2)
                    obj.write(3, 4, '', fmt_h2)
                    obj.write(3, 5, '=COUNTIF(F5:F10000, "ЗАДЕРЖАН")', fmt_h2)
                    obj.write(3, 6, f'=SUM(G5:G{row_idx})', fmt_h2_money)

    def __workbook_can_create(self):
        try:        # Using this cos xlsxwriter.Workbook don't raise error
            f_tmp = open(self.f_name, 'w')
        except Exception as err:
            self._to_log('{}', 1, err)
            return False
        else:
            f_tmp.close()
        return True

    def __sheet_create(self, name='main'):
        # Add headers formats
        fmt_h1 = self.__workbook.add_format({'bg_color': '#FEE0D0', **self.__fmt_h_def})
        fmt_big = self.__workbook.add_format({'font_size': '20', 'align': 'center', 'valign': 'vcenter' })

        if name == 'main':  # Sheet - Отчет
            self.__main_p = self.__workbook.add_worksheet('Отчет')
            # Adjust the column width.
            self.__main_p.set_column('A:A', 17)     # Date
            self.__main_p.set_column('B:B', 47)     # Address
            self.__main_p.set_column('C:C', 7.3)    # Court
            self.__main_p.set_column('D:D', 18)     # Registry
            self.__main_p.set_column('E:E', 36)     # C_SUM
            self.__main_p.set_column('F:F', 58)     # Comment
            self.__main_p.set_column('G:G', 11.3)   # Jail
            self.__main_p.set_column('H:H', 17)     # PaySum
            # Adjust the row height and freeze 2 rows.
            self.__main_p.set_row(0, 25)
            self.__main_p.set_row(1, 25)
            self.__main_p.freeze_panes(2, 0)
            self.__main_p.set_default_row(15)
            # Header
            self.__main_p.write('A1', 'ДАТА', fmt_h1)
            self.__main_p.write('B1', 'АДРЕС', fmt_h1)
            self.__main_p.write('C1', 'Участок', fmt_h1)
            self.__main_p.write('D1', 'РЕЕСТР', fmt_h1)
            self.__main_p.write('E1', 'Контрольная Сумма', fmt_h1)
            self.__main_p.write('F1', 'Комментарий', fmt_h1)
            self.__main_p.write('G1', 'Задержаний', fmt_h1)
            self.__main_p.write('H1', 'Сумма взысканий', fmt_h1)
        else:       # Sheet - Для руководства
            self.__ruk_p = self.__workbook.add_worksheet('Для руководства')
            # Adjust the column width.
            self.__ruk_p.set_column('A:A', 17)     # Date
            self.__ruk_p.set_column('B:B', 47)     # Address
            self.__ruk_p.set_column('C:C', 7.3)    # Court
            self.__ruk_p.set_column('D:D', 18)     # Registry
            self.__ruk_p.set_column('E:E', 58)     # Comment
            self.__ruk_p.set_column('F:F', 11.3)   # Jail
            self.__ruk_p.set_column('G:G', 17)     # PaySum
            # Adjust the row height and freeze 2 rows.
            self.__ruk_p.set_row(0, 21.75)
            self.__ruk_p.set_row(1, 21.75)
            self.__ruk_p.set_row(2, 25)
            self.__ruk_p.set_row(3, 25)
            self.__ruk_p.freeze_panes(4, 0)
            self.__ruk_p.set_default_row(15)
            # Header
            self.__ruk_p.merge_range('A1:G1', 'С П Р А В К А', fmt_big)
            self.__ruk_p.merge_range('A2:G2', f'по состоянию на {datetime.strftime(datetime.today(), "%d.%m.%Y")} года.', fmt_big)
            self.__ruk_p.write('A3', 'ДАТА', fmt_h1)
            self.__ruk_p.write('B3', 'АДРЕС', fmt_h1)
            self.__ruk_p.write('C3', 'Участок', fmt_h1)
            self.__ruk_p.write('D3', 'РЕЕСТР', fmt_h1)
            self.__ruk_p.write('E3', 'Комментарий', fmt_h1)
            self.__ruk_p.write('F3', 'Задержаний', fmt_h1)
            self.__ruk_p.write('G3', 'Сумма взысканий', fmt_h1)

        self._to_log('Sheet "{}" created.', 3, name)


if __name__ == '__main__':
    app = Excel('xaxaxa.xlsx')
    # Some data we want to write to the worksheet.
    app.data_from_db()
    #app.main_p_data = [()]
    '''
    app.main_p_data = [
     ['05.08.2019 12:28:22', 'г. Москва, ул. Красного Маяка, д. 13-б', 230, 'ФССП',
      'd421166fd142e331b0d8df3fe059d2f1', 'Сообщили в ФССП. Снят с базы.', '', '46352.13'],
     ['05.08.2019 12:38:15', 'г. Москва, ул. Красного Маяка, д. 13-б', 230, 'ФССП',
      'd421166fd142e331b0d8df3fe059d2f1', 'Сообщили в ФССП. Снят с базы.', '', '46352.13'],
     ['05.08.2019 14:38:11', 'г. Москва, ул. Красного Маяка, д. 13-б', 230, 'ФССП',
      'd421166fd142e331b0d8df3fe059d2f1', 'Сообщили в ФССП. Снят с базы.', '', '46352.13'],
     ['02.08.2019 10:08:34',  'г. Москва, пр-д Одоевского, д. 11, корп. 7',  62, 'ФССП',
      '3c20f2fe7dd784395ca0960e6a95db65', 'Сообщили приставу', 'ЗАДЕРЖАН', '85000.00'],
     ['02.08.2019 9:54:41', 'г. Москва, ул. Игральная, д. 5, корп. 1',  108, 'ФССП',
      'd4541a5af79fe38ef8d61df9f2b8e6b6', 'Сообщили в ФССП. Снят с базы.', '', '24015.00'],
     ['01.08.2019 17:47:02',  'г. Москва, ул. Кубанская, д. 23',   249, 'ФССП',
      '629b9f830a9ae0d2b7ec8d07b469babe', 'Сообщили приставу', '', '274124.86'],
     ['01.08.2019 15:49:12',  'г. Москва, ул. Верейская, д. 21',   196, 'МВД',
      'fe1650ebe436af099e103c0337633094', 'Сообщили приставу', '', '106000.00']
    ]
    '''



