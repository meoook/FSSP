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
        self.year.bind('<KeyRelease>', lambda event: self._release(event, 'year'))

    def _backspace(self, entry):
        cont = entry.get()
        entry.delete(0, tk.END)
        entry.insert(0, cont[:-1])

    def _press(self, event):
        event.widget.config(state='readonly')
        char = event.char
        keysum = event.keysym
        keycode = event.keycode
        type = event.type
        print(event.widget['width'])
        print('PRESS {}, KeySum: {}, KeyCode: {}, Event type: {}'.format(char, keysum, keycode, type))
        if event.keysym == 'BackSpace':
            print('Backspace pressed')
        elif char.isdigit():
            self.ttt.set(char)
            pass


    def _release(self, event, date_part=None):
        entry = event.widget
        print('date part', date_part)
        size = entry['width']
        entry.config(state='normal')
        data = entry.get()
        print('DATA', data)
        print('kesy', event.keysym)
        if data.isdigit():
            event.widget.config(state='normal')
        elif entry['width'] > 3:
            next_entry = self.winfo_name()
            print(next_entry)
            if len(data) > size > len(next_entry.get()):
                cont = entry.get()
                entry.delete(size, tk.END)
                to_next = cont[size:]
                next_entry.insert(0, to_next)
                print('DATA:', cont, '. Leave:', cont[:size], '. To next:', to_next)
                print('FACT:', cont, '. Leave:', entry.get(), '. To next:', next_entry.get())
                next_entry.focus()
            elif len(data) == size and next_entry:
                next_entry.focus()
        elif len(data) > size:
            self._backspace(entry)

    def _check2(self, index):
        entry = self.entries[index]
        bef_index = index - 1
        if not len(entry.get()) > 0 or bef_index < 0:
            bef_entry = self.entries[bef_index]
            if len(bef_entry.get()) > 1:
                self._backspace(bef_entry)
            bef_entry.focus()

    def get(self):
        return [e.get() for e in self.entries]


if __name__ == '__main__':
    win = tk.Tk()
    win.title('DateEntry demo')

    dentry = DateEntry()
    dentry.pack()

#    win.bind('<Return>', lambda e: print(dentry.get()))
    win.mainloop()
