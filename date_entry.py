import tkinter as tk

'''
Posible UPDATES

    monthlist1 = [1,3,5,7,8,10,12] ## monthlist for months with 31 days.
    monthlist2 = [4,6,9,11] ## monthlist for months with 30 days.
    monthlist3 = 2 ## month with month with 28 days.

    SETTING READ ONLY COLORS
'''


class DateEntry(tk.Label):      # tk.Frame as defaul but we need to translate Font
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ttt = tk.StringVar()
        self.day = tk.Entry(self, width=2, font=('Helvetica', 40, tk.NORMAL), border=0)
        self.dot_dm = tk.Label(self, text='.', font=('Helvetica', 40, tk.NORMAL), border=0, bg='white')
        self.month = tk.Entry(self, width=2, font=('Helvetica', 40, tk.NORMAL), border=0)
        self.dot_my = tk.Label(self, text='.', font=('Helvetica', 40, tk.NORMAL), border=0, bg='white')
        self.year = tk.Entry(self, width=4, font=('Helvetica', 40, tk.NORMAL), border=0, textvariable=self.ttt)

        self.day.pack(side=tk.LEFT)
        self.dot_dm.pack(side=tk.LEFT)
        self.month.pack(side=tk.LEFT)
        self.dot_my.pack(side=tk.LEFT)
        self.year.pack(side=tk.LEFT)

        self.day.bind('<KeyPress>', self._press)
        self.day.bind('<KeyRelease>', self._release)
        self.month.bind('<KeyPress>', self._press)
        self.month.bind('<KeyRelease>', self._release)
        self.year.bind('<KeyPress>', self._press)
        self.year.bind('<KeyRelease>', self._release)

        self.day.focus()        # DELETE

    @staticmethod
    def __backspace(part):
        cur = part.index('insert')
        print('backspace', part.get()[cur-1:cur])
        part.delete(cur-1, cur)

    @staticmethod
    def __delete(part):
        cur = part.index('insert')
        print('delete', part.get()[cur:cur+1])
        part.delete(cur, cur+1)

    @property
    def date(self):
        d, m, y = self.day.get(), self.month.get(), self.year.get()
        d = int(d) if d.isdigit() else 0
        m = int(m) if m.isdigit() else 0
        y = int(y) if y.isdigit() else 0
        return '{:02d}.{:02d}.{:04d}'.format(d, m, y)

    @date.setter
    def date(self, value):
        try:
            d, m, y = value.split('.')
        except Exception:
            print('Value not a date format dd.mm.yyyy Change it:', value)
        else:
            self.day.delete(0, tk.END)
            self.month.delete(0, tk.END)
            self.year.delete(0, tk.END)

            self.day.insert(0, d)
            self.month.insert(0, m)
            self.year.insert(0, y)

    def _press(self, event):
        print('======== PRESS =========')
        ww = event.widget
        ww.config(state='readonly')
        key = event.keysym
        v = ww.get()
        part = self.__day_part_detect(ww)
        cur_pos = ww.index('insert')
        selected = ww.selection_present()

        print('Position {}, width {}, KeySum: {}, Selected: {}'.format(cur_pos, ww['width'], key, selected))
        if selected and key.isdigit():          # SELECTED
            ww.config(state='normal')
        elif key == 'BackSpace':                # BACKSPACE
            if cur_pos == 0:
                if part[0]:                     # JUMPING TO PREV
                    part[0].focus()
                    self.__backspace(part[0])
            else:                               # CAN BACKSPACE IN CURRENT CELL
                ww.config(state='normal')
        elif key == 'Delete':                   # DELETE
            if cur_pos >= ww['width']:
                if part[1]:                     # JUMPING TO NEXT
                    part[1].focus()
                    part[1].icursor(0)
                    self.__delete(part[1])
            else:                               # CAN DELETE IN CURRENT CELL
                ww.config(state='normal')
        elif key.isdigit():                     # THE KEY IS DIGIT
            if len(v) >= ww['width']:           # THE CELL IS FULL
                if cur_pos >= ww['width']:      # CURSOR AT THE END.
                    if part[1]:                 # JUMPING TO NEXT
                        part[1].focus()
                        part[1].icursor(0)
                        if len(part[1].get()) >= part[1]['width']:  # NEXT IS FULL. REPLACE BEGINNING
                            self.__delete(part[1])
                            part[1].insert(0, key)
                        else:                   # FREE SPACE. INPUT HERE
                            part[1].insert(0, key)
                    else:                       # NO NEXT CELL TO ADD. REPLACE LAST
                        ww.config(state='normal')
                        self.__backspace(ww)
                else:                           # JUST REPLACE VALUE
                    ww.config(state='normal')
                    self.__delete(ww)
            elif len(v) + 1 >= ww['width']:     # WILL BE FULL AFTER INSERT
                ww.config(state='normal')
                if part[1]:                     # JUMPING TO NEXT
                    part[1].focus()
                    if len(part[1].get()) == part[1]['width']:  # NEXT IS FULL. SELECTING
                        part[1].selection_range(0, 'end')
            else:                               # THERE ARE ENOUGH FREE SELLS. INPUT HERE.
                ww.config(state='normal')
        elif key == 'Left' and cur_pos == 0 and part[0]:
            part[0].focus()
        elif key == 'Right' and cur_pos >= ww['width'] and part[1]:
            part[1].focus()
        elif key in ('Alt_R', 'Alt_L', 'Control_L', 'Control_R'):
            self.day.unbind_all()
            self.month.unbind_all()
            self.year.unbind_all()
        else:
            print('NOT A VALID INPUT')

    def _release(self, event):          # THIS DEF NEEDS REMAKE
        print('======= RELEASE ========')
        self.day.config(state='normal')
        self.month.config(state='normal')
        self.year.config(state='normal')
        d, m, y = self.day.get(), self.month.get(), self.year.get()
        d = int(d) if d.isdigit() else 0
        m = int(m) if m.isdigit() else 0
        y = int(y) if y.isdigit() else 0
        if 9 < d > 31:
            self.day.config(bg='#F77')
            self.day.delete(0, tk.END)
            self.day.insert(0, '31')
        else:
            self.day.config(bg='white')
        if 9 < m > 12:
            self.month.config(bg='#F77')
            self.month.delete(0, tk.END)
            self.month.insert(0, '12')
        else:
            self.month.config(bg='white')
        if y > 999 and (1900 > y or y > 2100):
            self.year.config(bg='#F77')
            self.year.delete(0, tk.END)
            self.year.insert(0, '20' + str(y)[2:])
        else:
            self.year.config(bg='white')
        print('Final:', self.date)

    def __day_part_detect(self, widget):    # Возвращает право и лево от текущей ячейки
        before = False
        nxt = False
        if widget == self.day:
            nxt = self.month
        elif widget == self.month:
            before = self.day
            nxt = self.year
        elif widget == self.year:
            before = self.month
        return [before, nxt]


if __name__ == '__main__':
    win = tk.Tk()
    win.title('DateEntry demo')
    win.geometry('+2700+500')

    dentry = DateEntry()
    dentry.pack()

#    win.bind('<Return>', lambda e: print(dentry.get()))
    win.mainloop()
