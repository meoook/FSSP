import tkinter as tk
from tkinter import ttk, Button
import psycopg2


class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.add_img = tk.PhotoImage(file='.\img\windows.gif')
        self.init_main()
        self.db = db
        self.view_records()

    def init_main(self):
        toolbar = tk.Frame(bg='#d3d3d3', bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        btn_open_dialog = tk.Button(toolbar, text='Add position', command=self.open_dialog, bg="#f4f4f4", bd=0,
                                    compound=tk.TOP, image=self.add_img)
        btn_open_dialog.pack(side=tk.LEFT)

        self.tree = ttk.Treeview(self, column=('dt', 'adr', 'court', 'rst', 'csum', 'comm', 'jail', 'sum'),
                                 height=10, show='headings', padding=0, selectmode='browse')

        self.tree.column('dt', width=110, anchor=tk.CENTER)
        self.tree.column('adr', width=250, anchor=tk.W)
        self.tree.column('court', width=55, anchor=tk.CENTER)
        self.tree.column('rst', width=50, anchor=tk.CENTER)
        self.tree.column('csum', width=130, anchor=tk.W)
        self.tree.column('comm', width=250, anchor=tk.CENTER, stretch=True)
        self.tree.column('jail', width=80, anchor=tk.CENTER)
        self.tree.column('sum', width=110, anchor=tk.CENTER)

        self.tree.heading('dt', text='Время')
        self.tree.heading('adr', text='Адрес')
        self.tree.heading('court', text='Участок')
        self.tree.heading('rst', text='Реестр')
        self.tree.heading('csum', text='Контрольная сумма')
        self.tree.heading('comm', text='Комментарий')
        self.tree.heading('jail', text='Задержаний')
        self.tree.heading('sum', text='Сумма взысканий')

        print(ttk.Style().theme_names())
        ttk.Style().theme_use('default')
        self.tree.grid(row=50, column=5)

        self.tree.pack()

    def records(self, description, cost, total):
        self.db.insert_data(description, cost, total)
        self.view_records()

    def view_records(self):
        # Делаем SELECT
        select = "SELECT upper(lastname), upper(firstname), upper(secondname), to_char(birthday, 'DD.MM.YYYY'), " \
                 "to_char(creation_date, 'DD.MM.YYYY hh24:mi:ss'), court_adr, court_numb, reestr, " \
                 "md5(concat(upper(lastname), upper(firstname), upper(secondname), to_char(birthday, 'DD.MM.YYYY'))) " \
                 "FROM fssp as v WHERE creation_date::date >= '24.05.2019'"
#        select += "=" if znak == 'eq' else ">="
#        select += "current_date " if date == 'xx' else "'" + date + "'"  # Нужна проверочка - что date соответсвует формату
        self.db.cur.execute(select)
        [self.tree.delete(i) for i in self.tree.get_children()]
        [self.tree.insert('', 'end', values = row[4:]) for row in self.db.cur.fetchall()]

    def open_dialog(self):
        Child()


class Child(tk.Toplevel):
    def __init__(self):
        super().__init__(root)
        self.init_child()
        self.view = app

    def init_child(self):
        self.title('Добавить доходы\расходы')
        self.geometry('400x220+400+300')
        self.resizable(False, False)

        label_description = tk.Label(self, text='Наименование')
        label_description.place(x=50, y=50)
        label_select = tk.Label(self, text='Доходы\Расходы')
        label_select.place(x=50, y=80)
        label_summ = tk.Label(self, text='Сумма:')
        label_summ.place(x=50, y=110)

        self.entry_description = ttk.Entry(self)
        self.entry_description.place(x=200, y=50)

        self.combobox = ttk.Combobox(self, values=[u'Доход', u'Расход'])
        self.combobox.current(0)
        self.combobox.place(x=200, y=80)

        self.entry_money = ttk.Entry(self)
        self.entry_money.place(x=200, y=110)

        btn_ok = ttk.Button(self, text='Добавить')
        btn_ok.place(x=220, y=170)
        btn_ok.bind('<Button-1>', lambda event: self.view.records(self.entry_description.get(),
                                                                  self.entry_money.get(),
                                                                  self.combobox.get()))

        btn_cancel = ttk.Button(self, text='Отмена', command=self.destroy)
        btn_cancel.place(x=300, y=170)

        # Захват окна
        self.grab_set()
        self.focus_get()


class DB:
    def __init__(self):
        self.conn = psycopg2.connect(host='localhost', user='postgres', password=111, database='skuns')
        self.cur = self.conn.cursor()

    def insert_data(self, description, cost, total):
        self.cur.execute('INSERT INTO finance(description, costs, total) VALUES (?, ?, ?)', (description, cost, total))


if __name__ == '__main__':
    root = tk.Tk()
    db = DB()
    app = Main(root)
    app.pack()
    root.title("My GUI Test")
    root.geometry('1070x400+300+200')
    root.resizable(False, False)
    root.mainloop()
