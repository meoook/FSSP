from __future__ import print_function

import tkinter as tk


class DateEntry(tk.Frame):
    def __init__(self):
        super().__init__()
        self.entry_1 = tk.Entry(self, width=2, font=('Helvetica', 40, tk.NORMAL), border=0)
        self.label_1 = tk.Label(self, text='.', font=('Helvetica', 40, tk.NORMAL), border=0, bg='white')
        self.entry_2 = tk.Entry(self, width=2, font=('Helvetica', 40, tk.NORMAL), border=0)
        self.label_2 = tk.Label(self, text='.', font=('Helvetica', 40, tk.NORMAL), border=0, bg='white')
        self.entry_3 = tk.Entry(self, width=4, font=('Helvetica', 40, tk.NORMAL), border=0)

        self.entry_1.pack(side=tk.LEFT)
        self.label_1.pack(side=tk.LEFT)
        self.entry_2.pack(side=tk.LEFT)
        self.label_2.pack(side=tk.LEFT)
        self.entry_3.pack(side=tk.LEFT)

        self.entries = [self.entry_1, self.entry_2, self.entry_3]

        self.entry_1.bind('<KeyRelease>', lambda e: self._check(0, 2))
        self.entry_2.bind('<KeyRelease>', lambda e: self._check(1, 2))
        self.entry_2.bind('<BackSpace>', lambda e: self._check2(1))
        self.entry_3.bind('<KeyRelease>', lambda e: self._check(2, 4))
        self.entry_3.bind('<BackSpace>', lambda e: self._check2(2))

    def _backspace(self, entry):
        cont = entry.get()
        entry.delete(0, tk.END)
        entry.insert(0, cont[:-1])

    def _check(self, index, size):
        entry = self.entries[index]
        data = entry.get()
        print('DATA', data)

        next_index = index + 1
        if not data.isdigit():
            self._backspace(entry)
        elif next_index < len(self.entries):
            next_entry = self.entries[next_index]
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
