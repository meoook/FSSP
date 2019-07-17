from __future__ import print_function

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

    @staticmethod
    def __backspace(part):
        cont = part.get()
        part.delete(0, tk.END)
        print('to del', cont[:part['width']-1])
        part.insert(0, str(cont[:part['width']-1]))
        print(part.get())

    def _press(self, event):
        #print('======= RELEASE ========')
        print('======== PRESS =========')
        ww = event.widget
        ww.config(state='readonly')
        key = event.keysym
        v = ww.get()
        part = self.__day_part_detect(ww)
        cursor_position = ww.index('insert')
        selected = ww.selection_present()
        print('whoo?', ww['state'])

        print('Position {}, KeySum: {}, Selected: {}'.format(cursor_position, key, selected))
        print('key type:', type(key))
        if key == 'BackSpace':        # , 'Delete'
            print('BackSpace')
            ww.config(state='normal')
            if cursor_position == 0:
                if part[0]:
                    part[0].focus()
                    self.__backspace(part[0])
            else:
                self.__backspace(ww)
        elif key.isdigit():
            print('len', len(v), 'width', ww['width'])
            if selected:
                print('clear')
                #ww.selection_clear()  # Clears the selection.
                ww.config(state='normal')
            elif (len(v) + 1 >= ww['width'] or ww['width'] == 0) and part[1]:
                ww.config(state='normal')
                part[1].focus()
                if len(part[1].get()) == part[1]['width']:
                    part[1].selection_range(0, 'end')
            else:
                ww.config(state='normal')
        else:
            print('OKOK')
        print('why', ww.get())

    def _release(self, event):
        print('======= RELEASE ========')
        #print('======== PRESS =========')
        event.widget.config(state='normal')

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

    dentry = DateEntry()
    dentry.pack()

#    win.bind('<Return>', lambda e: print(dentry.get()))
    win.mainloop()
