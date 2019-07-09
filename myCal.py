import calendar
import tkinter as tk
from tkinter import ttk
import time

print(time.localtime())

day, month, year = time.strftime("%d.%m.%Y", time.localtime()).split('.')


print(day)
print(month)
print(year)
'''

class DatePicker(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.selected_y = 
        self.cal = calendar.TextCalendar(firstweekday=0).itermonthdays4(self.selected_y, self.selected_m)

        self.cal.itermonthdays4(2019, 9)

'''

# Create Calendar obj
cal = calendar.TextCalendar(firstweekday=0)

# Locale Settings
month_names = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль',
               'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
week_names = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

# print(calendar.weekday(2019, 7, 8))   # Returns day of the week

def ggg(event):
    ww = event.widget
    text = ww['text']
    if text == 20:
        print('Quit')
        root.quit()
    print(text, ww['state'])
    ww.config(state="active")
    print(event.widget)

def ttt(event):
    event.widget.config(background='#BBB')

def xxx(event):
    event.widget.config(background='#DDD')

def motion(event):
    print("Mouse position: (%s %s)" % (event.x, event.y))

root = tk.Tk()
root.title('Tk Calendar')
root.config(bg='lightblue')
root.resizable(False, False)
#root.overrideredirect(1)
root.bind('<Button-1>', ggg)
#root.bind('<Motion>', motion)
cal_frame = tk.Frame(root)
cal_frame.grid()


# custom ttk styles
style = ttk.Style()
arrow_layout = lambda direrction: ([('Button.focus', {'children': [('Button.%sarrow' % direrction, None)]})])
style.layout('L.TButton', arrow_layout('left'))
style.layout('R.TButton', arrow_layout('right'))


lbtn = ttk.Button(cal_frame, style='L.TButton').grid(row=0, column=0,)
rbtn = ttk.Button(cal_frame, style='R.TButton').grid(row=0, column=3,)


for a in range(len(week_names)):
    tk.Label(cal_frame, text=week_names[a], width=2, anchor=tk.CENTER).grid(row=1, column=a, ipadx=3, ipady=1)

row = 2
for z, a in enumerate(cal.itermonthdays4(2019, 9)):
    column = a[3]
    current = tk.Label(cal_frame, text=a[2], relief=tk.RIDGE, width=2, anchor=tk.CENTER,  # style="C.TLabel",
             background='#DDD', foreground='#111', activebackground='#333', activeforeground='#FFF', disabledforeground='#AAA',
             highlightcolor='#F00', highlightbackground='#00F', highlightthickness=2, font=('Courier', 14), #, 'italic'), # Lucida Console
             state='normal',  # active/normal/disabled
             borderwidth=1, cursor='hand2', takefocus=1)
    current.grid(row=row, column=column, ipadx=4, ipady=2)    #SUNKEN/RIDGE/FLAT
    current.bind('<Enter>', ttt)
    current.bind('<Leave>', xxx)
#    current.bind('<Leave>', lambda event, bg='#ddd': current.config(background=bg))

    row = row + 1 if column == 6 else row

cal_frame.mainloop()





