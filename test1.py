import tkinter as tk


class DateEntry(tk.Frame):
    def __init__(self):
        super().__init__()
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

        self.day.focus()

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

    @staticmethod
    def __replace(part, key):
        v = part.get()
        cur = part.index('insert')
        cur = cur - 1 if cur >= part['width'] else cur
        print('replace in {} value {} on {}'.format(v, v[cur:cur+1], key))
        part.delete(cur, cur+1)
        print('1', part.get())
        part.insert(cur, key)
        print('2', part.get())

    def _press(self, event):
        print('======== PRESS =========')
        ww = event.widget
        ww.config(state='readonly')
        key = event.keysym
        v = ww.get()
        part = self.__day_part_detect(ww)
        cursor_position = ww.index('insert')
        selected = ww.selection_present()

        print('Position {}, width {}, KeySum: {}, Selected: {}'.format(cursor_position, ww['width'], key, selected))
        if selected and key.isdigit():
            print('SELECTED')
            # ww.selection_clear()  # Clears the selection.
            ww.config(state='normal')
        elif key == 'BackSpace':        # , 'Delete'
            print('BACKSPACE')
            if cursor_position == 0:
                if part[0]:
                    print('JUMPING TO PREV')
                    part[0].focus()
                    self.__backspace(part[0])
            else:
                print('STATE NORMAL')
                ww.config(state='normal')
        elif key == 'Delete':
            print('DELETE')
            if cursor_position >= ww['width']:
                if part[1]:
                    print('JUMPING TO NEXT')
                    part[1].focus()
                    part[1].icursor(0)
                    self.__delete(part[1])
            else:
                print('STATE NORMAL')
                ww.config(state='normal')
        elif key.isdigit():
            print('THE KEY IS DIGIT')
            if len(v) >= ww['width']:
                print('THE CELL IS FULL')
                if cursor_position >= ww['width']:
                    print('CURSOR AT THE END.')
                    if part[1]:
                        print('JUMPING TO NEXT')
                        part[1].focus()
                        print('HERE WE NEED TO INSERT NORM VALUE')
                    else:
                        print('NO NEXT CELL TO ADD. REPLACE LAST')
                        ww.config(state='normal')
                        self.__backspace(ww)
                        print('value', v)
                else:
                    print('JUST REPLACE VALUE')
                    ww.config(state='normal')
                    self.__delete(ww)
                    print('value', v)
            elif len(v) + 1 >= ww['width']:
                print('WILL BE FULL AFTER INSERT')
                ww.config(state='normal')
                if part[1]:
                    print('JUMPING TO NEXT')
                    part[1].focus()
                    if len(part[1].get()) == part[1]['width']:
                        print('NEXT IS FULL. SELECTING')
                        part[1].selection_range(0, 'end')
                else:
                    print('NO NEXT CELL TO JUMP')   # Here we can put CHECK_DATE
            else:
                print('THERE ARE ENOUGH FREE SELLS. INPUT HERE.')
                ww.config(state='normal')
        elif key == 'Left' and cursor_position == 0 and part[0]:
            part[0].focus()
        elif key == 'Right' and cursor_position >= ww['width'] and part[1]:
            part[1].focus()
        else:
            print('NOT A VALID INPUT')

    def _release(self, event):
        print('======= RELEASE ========')
        self.day.config(state='normal')
        self.month.config(state='normal')
        self.year.config(state='normal')
        print('Final: {}.{}.{}'.format(self.day.get(), self.month.get(), self.year.get()))

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
    win.geometry('+500+300')

    dentry = DateEntry()
    dentry.pack()

#    win.bind('<Return>', lambda e: print(dentry.get()))
    win.mainloop()
