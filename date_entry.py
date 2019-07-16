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

    def _backspace(self, part):
        cont = part.get()
        part.focus()
        part.delete(0, tk.END)
        part.insert(0, cont[:-1])

    def _release(self, event):
#        print('======== PRESS =========')
        print('======= RELEASE ========')
        event.widget.config(state='normal')
        ww = event.widget
        part = self.__day_part_detect(ww)
        if len(ww.get()) >= event.widget['width']:
            ww.selection_range(0, 'end')
            part[1].focus()
            if len(part[1].get()) == part[1]['width']:
                part[1].selection_range(0, 'end')

    def _press(self, event):
        print('======== PRESS =========')
#        print('======= RELEASE ========')
        event.widget.config(state='readonly')
        ww = event.widget
        char = event.char
        key = event.keysym
        v = ww.get()
        part = self.__day_part_detect(ww)
        cursor_position = ww.index('insert')
        print('Position {}, KeySum: {}'.format(cursor_position, key))

        selected = ww.selection_present()

        if key in ('BackSpace', 'Delete'):
            if len(v) == 0 and part[0]:     # Если ячейка пустая и есть слева ячейка
                self._backspace(part[0])
        elif len(v) <= event.widget['width']:
            if part[1]:
                ww.config(state='normal')
                part[1].focus()
            elif selected:
                ww.selection_clear()    # Clears the selection.
        elif char.isdigit():
            pass

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
