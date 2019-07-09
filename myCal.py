import calendar
import tkinter as tk
from tkinter import ttk

# Create Calendar obj
cal = calendar.TextCalendar(firstweekday=0)

print(cal.monthdayscalendar(2019, 9))

# Locale Settings
month_names = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль',
               'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
week_names = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

# print(calendar.weekday(2019, 7, 8))   # Returns day of the week

def ggg(event):
    ww = event.widget
    print(ww.cget("text"), ww['state'])
    ww.config(state="active")

root = tk.Tk()
root.title('Ttk Calendar')
root.resizable(False, False)
root.bind('<Button-1>', ggg)
cal_frame = ttk.Frame(root)
cal_frame.grid()

for a in range(len(week_names)):
    ttk.Label(cal_frame, text=week_names[a], width=2, anchor=tk.CENTER).grid(row=0, column=a, ipadx=3, ipady=1)

row = 1
days_all = {}
for z, a in enumerate(cal.itermonthdays4(2019, 9)):
    column = a[3]
    days_all[z] = tk.Label(cal_frame, text=a[2], relief=tk.RIDGE, width=2, anchor=tk.CENTER,  # style="C.TLabel",
             background='#DDD', foreground='#111', activebackground='#333', activeforeground='#FFF', disabledforeground='#AAA',
             highlightcolor='#F00', highlightbackground='#00F', highlightthickness=2,
             state='normal',  # active/normal/disabled
             borderwidth=4, cursor='hand2', takefocus=1).grid(row=row, column=column, ipadx=16, ipady=8)    #SUNKEN/RIDGE/FLAT

    row = row + 1 if column == 6 else row

canvas = tk.Canvas(root, height=20, bg='#002')
canvas.config(bg='#CCC', selectbackground='#F00')
canvas.grid()
canvas.create_text(10, 10, text='Test', activefill='#FFF', disabledfill='#999')

cal_frame.mainloop()
