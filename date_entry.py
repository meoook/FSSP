import tkinter as tk

'''
Can be deleted
Posible UPDATES

    monthlist1 = [1,3,5,7,8,10,12] ## monthlist for months with 31 days.
    monthlist2 = [4,6,9,11] ## monthlist for months with 30 days.
    monthlist3 = 2 ## month with month with 28 days.

    SETTING READ ONLY COLORS
'''


class DateEntry(tk.Label):      # tk.Frame as defaul but we need to translate Font
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__day = tk.Entry(self, width=2, **kwargs)
        bg = self.__day['bg']
        self.__day.config(readonlybackground=bg)
        dot_dm = tk.Label(self, text='.', **kwargs)
        self.__month = tk.Entry(self, width=2, readonlybackground=bg, **kwargs)
        dot_my = tk.Label(self, text='.', **kwargs)
        self.__year = tk.Entry(self, width=4, readonlybackground=bg, **kwargs)

        self.__day.pack(side=tk.LEFT)
        dot_dm.pack(side=tk.LEFT)
        self.__month.pack(side=tk.LEFT)
        dot_my.pack(side=tk.LEFT)
        self.__year.pack(side=tk.LEFT)

        self.__day.bind('<KeyPress>', self._press)
        self.__day.bind('<KeyRelease>', self._release)
        self.__month.bind('<KeyPress>', self._press)
        self.__month.bind('<KeyRelease>', self._release)
        self.__year.bind('<KeyPress>', self._press)
        self.__year.bind('<KeyRelease>', self._release)

    @staticmethod
    def __backspace(part):
        cur = part.index('insert')
        part.delete(cur-1, cur)

    @staticmethod
    def __delete(part):
        cur = part.index('insert')
        part.delete(cur, cur+1)

    @property
    def date(self):
        d, m, y = self.__day.get(), self.__month.get(), self.__year.get()
        d = int(d) if d.isdigit() else 0
        m = int(m) if m.isdigit() else 0
        y = int(y) if y.isdigit() else 0
        return '{:02d}.{:02d}.{}'.format(d, m, y)

    @date.setter
    def date(self, value):
        try:
            d, m, y = value.split('.')
        except Exception as e:
            print('Value not a date format dd.mm.yyyy Change it:', value, e)
        else:
            self.__day.delete(0, tk.END)
            self.__month.delete(0, tk.END)
            self.__year.delete(0, tk.END)

            self.__day.insert(0, d)
            self.__month.insert(0, m)
            self.__year.insert(0, y)

    def __day_part_detect(self, widget):    # Возвращает право и лево от текущей ячейки
        before = False
        nxt = False
        if widget == self.__day:
            nxt = self.__month
        elif widget == self.__month:
            before = self.__day
            nxt = self.__year
        elif widget == self.__year:
            before = self.__month
        return [before, nxt]

    def _press(self, event):
        ww = event.widget                   # Current cell object
        ww.config(state='readonly')         # Make cell readonly (no input allowed but visible cursor
        key = event.keysym                  # Input key (what key was pressed)
        v = ww.get()                        # Value inside the cell
        wth = ww['width']                   # Maximum digits in the cell
        part = self.__day_part_detect(ww)   # Objects: before and next cells or False
        cur_pos = ww.index('insert')        # Cursor position
        selected = ww.selection_present()   # If anything selected in the cell

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
            if cur_pos >= wth or (cur_pos == 0 and len(v) == 0):
                if part[1]:                     # JUMPING TO NEXT
                    part[1].focus()
                    part[1].icursor(0)
                    self.__delete(part[1])
            else:                               # CAN DELETE IN CURRENT CELL
                ww.config(state='normal')
        elif key.isdigit():                     # THE KEY IS DIGIT
            if len(v) >= wth:                   # THE CELL IS FULL
                if cur_pos >= wth:              # CURSOR AT THE END
                    if part[1]:                 # JUMPING TO NEXT
                        part[1].focus()
                        part[1].icursor(0)
                        if len(part[1].get()) >= part[1]['width']:  # NEXT IS FULL
                            self.__delete(part[1])
                            part[1].insert(0, key)      # REPLACE FIRST
                        else:                   # ENOUGH FREE SPACE. INPUT HERE.
                            part[1].insert(0, key)
                    else:                       # NO NEXT CELL TO ADD. REPLACE LAST
                        ww.config(state='normal')
                        self.__backspace(ww)
                else:                           # REPLACE VALUE
                    ww.config(state='normal')
                    self.__delete(ww)
            elif len(v) + 1 >= wth:             # WILL BE FULL AFTER INSERT
                ww.config(state='normal')
                if part[1]:                     # JUMPING TO NEXT
                    part[1].focus()
                    if len(part[1].get()) == part[1]['width']:  # NEXT IS FULL. SELECTING
                        part[1].selection_range(0, 'end')
            else:                               # THERE ARE ENOUGH FREE SELLS. INPUT HERE.
                ww.config(state='normal')
        elif key == 'Left' and cur_pos == 0 and part[0]:                                         # NAVIGATION <<<
            part[0].focus()
        elif key == 'Right' and part[1] and (cur_pos >= wth or (cur_pos == 0 and len(v) == 0)):  # NAVIGATION >>>
            part[1].focus()
        elif key in ('Alt_R', 'Alt_L', 'Control_L', 'Control_R'):   # Need to turn off key combinations
            pass

    def _release(self, event):          # THIS DEF NEEDS REMAKE
        self.__day.config(state='normal')
        self.__month.config(state='normal')
        self.__year.config(state='normal')
        d, m, y = self.__day.get(), self.__month.get(), self.__year.get()
        d = int(d) if d.isdigit() else 0
        m = int(m) if m.isdigit() else 0
        y = int(y) if y.isdigit() else 0
        if 9 < d > 31:
            self.__day.config(bg='#F77')
            self.__day.delete(0, tk.END)
            self.__day.insert(0, '31')
        else:
            self.__day.config(bg='white')
        if 9 < m > 12:
            self.__month.config(bg='#F77')
            self.__month.delete(0, tk.END)
            self.__month.insert(0, '12')
        else:
            self.__month.config(bg='white')
        if y > 999 and (1900 > y or y > 2100):      # Пока не будет 4 знака (999)
            self.__year.config(bg='#F77')
            self.__year.delete(0, tk.END)
            self.__year.insert(0, '20' + str(y)[2:])
        else:
            self.__year.config(bg='white')


if __name__ == '__main__':
    win = tk.Tk()
    win.title('DateEntry demo')
    #win.geometry('+2700+500')
    win.geometry('+600+400')

    dentry = DateEntry(font=('Helvetica', 45, tk.NORMAL), border=0)
    dentry.pack()
    dentry.date = '10.10.2005'
    win.mainloop()
