import sqlite3
import datetime


class DB:
    def __init__(self):
        self.__db = sqlite3.connect('fssp.db', timeout=5, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.__db.isolation_level = None
        self.__c = self.__db.cursor()

        self.__c.execute(
            '''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY,
                                                 first TEXT,
                                                 name TEXT,
                                                 second TEXT,
                                                 dr DATE,
                                                 c_sum CHAR(32))''')
        self.__c.execute(   # SELECT time AS "time [TIMESTAMP]" FROM u_visits
            '''CREATE TABLE IF NOT EXISTS visits (time TIMESTAMP PRIMARY KEY,
                                                    u_id INTEGER REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
                                                    adr TEXT,
                                                    court INTEGER,
                                                    registry TEXT,
                                                    comment TEXT,
                                                    jail TEXT)''')   # AUTOINCREMENT
        self.__c.execute(
            '''CREATE TABLE IF NOT EXISTS sums (u_id INTEGER REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
                                                    update_date DATE,
                                                    v_time TIMESTAMP REFERENCES visits(time) ON UPDATE CASCADE,
                                                    sum REAL)''')
        self.__c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS sums_IDX ON sums (u_id,update_date)''')
        self.__get_table()

    @property
    def schema(self):
        """ To show all tables """
        self.__c.execute('SELECT * FROM sqlite_master')  # like .schema
        print(self.__c.fetchall())
        return self.__c.fetchall()

    def __get_table(self):
        """ Get array of control sums """
        self.__c.execute('''SELECT c_sum FROM users''')
        self.__u_sums = [x[0] for x in self.__c.fetchall()]

    @property
    def table(self):
        """ Return all visits (to insert in other class like tk.treeview) """
        self.__c.execute('''SELECT u."first", u.name, u.second, u.dr, u.c_sum, v.time, v.adr, v.court, v.registry,
         v.comment, v.jail, s.sum FROM visits AS v LEFT JOIN users AS u ON u.id=v.u_id 
         LEFT JOIN sums as s ON v.time=s.v_time AND s.u_id = u.id''')
        return self.__c.fetchall()

    @table.setter
    def table(self, array):
        """ Input array: F, I, O, dr, control sum, time, adr, court, registry
            Check if user or visit already exist and then add user or\and visit
        """
        for row in array:
            if len(row) == 9:
                if row[4] in self.__u_sums:
                    self.__c.execute('''SELECT id FROM users WHERE c_sum=?''', (row[4], ))
                    last = self.__c.fetchone()[0]
                else:
                    print('Adding user', *row[:5])
                    self.__c.execute('''INSERT INTO users(first, name, second, dr, c_sum) VALUES (?, ?, ?, ?, ?)''',
                                     (row[0].upper(), row[1].upper(), row[2].upper(), row[3], row[4]))
                    last = self.__c.lastrowid
                    self.__get_table()  # After adding - update u_sums
                self.__c.execute('''SELECT time, u_id FROM visits WHERE time=? AND u_id=?''', (row[5], last))
                if len(self.__c.fetchall()) > 0:
                    print('THIS ROW ALREADY EXIST')
                else:
                    self.__c.execute('''INSERT INTO visits (time, u_id, adr, court, registry)
                                        VALUES (?, ?, ?, ?, ?)''', (row[5], last, row[6], row[7], row[8]))

    def insert_data(self, data, u_id, time=None, column='sum'):
        # ПЕРЕДЕЛАТЬ ЛОГИКУ ДЛЯ ВСТАВКИ СУММЫ
        # ПЕРЕДЕЛАТЬ ЛОГИКУ ДЛЯ ВСТАВКИ СУММЫ
        # ПЕРЕДЕЛАТЬ ЛОГИКУ ДЛЯ ВСТАВКИ СУММЫ
        # ПЕРЕДЕЛАТЬ ЛОГИКУ ДЛЯ ВСТАВКИ СУММЫ
        # ПЕРЕДЕЛАТЬ ЛОГИКУ ДЛЯ ВСТАВКИ СУММЫ
        # ПЕРЕДЕЛАТЬ ЛОГИКУ ДЛЯ ВСТАВКИ СУММЫ
        # ПЕРЕДЕЛАТЬ ЛОГИКУ ДЛЯ ВСТАВКИ СУММЫ
        if column == 'comment':
            self.__c.execute('''UPDATE visits SET comment=? WHERE time=? AND u_id=?''', (data, time, u_id))
        elif column == 'jail':
            self.__c.execute('''UPDATE visits SET jail=? WHERE time=? AND u_id=?''', (data, time, u_id))
        else:
            self.__c.execute('''UPDATE sums SET sum=? WHERE update_date=? AND u_id=?''',
                             (data, datetime.date.today(), u_id))
            if self.__c.rowcount == 0:
                self.__c.execute('''INSERT INTO sums(u_id, update_date, v_time, sum) VALUES (?, ?, ?, ?)''',
                                 (u_id, datetime.date.today(), time, data))


if __name__ == '__main__':
    app = DB()
    app.table = [('lebedev', 'artem', 'mudakovich', '1984-09-30', 'd4afs3j5fhz3a5d57sdf481ay7fa1k3b',
                 '2019-08-06 14:26:58', 'Moscow 1905 St. 1945 112', 353, 'FSSP'),
                 ('petrov', 'vasiliy', 'alexeevich', '1934-02-06', 'g4a7s4a5zgz6a53ads8f411ay5fa6kjp',
                  '2019-08-07 22:11:33', 'Moscow 1905 Serbskaya 2', 123, 'FSSP'),
                 ('kuznecova', 'irina', 'anatolevna', '1989-08-30', '53ads3j5fhz3z5357sdf48sa07fa9kaz',
                  '2019-08-08 10:12:08', 'Moscow 1905 Sadovaya 45', 153, 'FSSP')]
    [print(x) for x in app.table]

    app.insert_data(18367.54, 1, '2019-08-06 14:26:58')
    app.insert_data(132121.24, 2, '2019-08-07 15:34:21')
    app.insert_data(99921.24, 3, '2019-08-08 10:12:08')
    app.insert_data('ЗАДЕРЖАН', 2, '2019-08-07 15:34:21', 'jail')
    app.insert_data('ЗАДЕРЖАН', 3, '2019-08-07 15:34:21', 'jail')
    app.insert_data('Сообщили приставу', 3, '2019-08-08 09:12:08', 'comment')
    app.insert_data('Сприставу', 2, '2019-08-08 09:12:08', 'comment')


