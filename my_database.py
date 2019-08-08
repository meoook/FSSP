import sqlite3
import psycopg2
from my_colors import Color


class DataBase:
    """ Data base class. Only for FSSP_checker """
    def __init__(self, db_connect=None, log_handler=None):
        self.__conn = None
        self.__cur = None
        # Прикручиваем LOGGER
        if log_handler is None:
            def log_pass(*args, **kwargs):
                print('DataBase class ERROR: Log handler not found.', *args)

            self.__to_log = log_pass
        else:
            self.__to_log = log_handler

        if db_connect:
            self.open(db_connect)

    def open(self, pa):  # Parameters
        try:
            self.__conn = psycopg2.connect(host=pa['host'], database=pa['dbname'], user=pa['user'], password=pa['pwd'],
                                           connect_timeout=1)
        except psycopg2.Error as error:
            self.__to_log('DB ERROR {}', 1, str(error)[:-1], c1=Color.zero)
            self.__conn = None
            self.__cur = None
        else:
            self.__cur = self.__conn.cursor()
            self.__to_log('DB connected - {}', 3, 'OK', c1=Color.ok)

    # Делаем SELECT
    def select_sql(self, date):
        """ Get visits """
        if not self.__conn:
            self.__to_log('Unable to select. Db connection error.', 2)
            return False
        date = date if (date and date.count('.') == 2 and len(date) == 10 | 18) else '18.02.2019'  # Start tracking date
        # Home version
        select = "SELECT upper(lastname), upper(firstname), upper(secondname), to_char(birthday, 'DD.MM.YYYY'), " \
                 "md5(concat(upper(lastname), upper(firstname), upper(secondname), to_char(birthday, 'DD.MM.YYYY'))), " \
                 "creation_date, court_adr, court_numb, reestr " \
                 f"FROM fssp as v WHERE creation_date > '{date}' ORDER BY v.creation_date DESC"
        # work version
        '''
        select = "SELECT " \
                 "upper(v.last_name), upper(v.first_name), upper(v.patronymic), to_char(v.birthdate, 'DD.MM.YYYY'), " \
                 "to_char(c.creation_date, 'DD.MM.YYYY hh24:mi:ss'), o.address, u.\"number\", " \
                 "CASE WHEN mia_check_result = 1 THEN 'МВД' ELSE 'ФССП' END, " \
                 "md5(concat(upper(v.last_name), upper(v.first_name), upper(v.patronymic), v.birthdate::date)) " \
                 "FROM visitor_violation_checks AS c " \
                 "RIGHT JOIN visitors AS v ON c.visitor_id = v.id " \
                 "RIGHT JOIN court_objects AS o ON v.court_object_id = o.id " \
                 "RIGHT JOIN court_stations AS u ON v.court_station_id = u.id " \
                 "WHERE v.court_object_id not IN (173, 174) " \
                 "AND (mia_check_result = 1 OR fssp_check_result = 1) " \
                 f"AND v.creation_date > {date} ORDER BY v.creation_date DESC"
        '''
        self.__cur.execute(select)
        self.__to_log('SQL request return {} rows. Conditions: {}', 3,
                      str(self.__cur.rowcount), select[288:-29].upper(), c1=Color.inf, c2=Color.info)
        # , 3, str(self.cur.rowcount), select[632:-29].upper(), c1='#EE4', c2='#EE4')
        return self.__cur.fetchall()

    # Закрываем соединение с БД - не понятно, работает ли :)
    def close(self):
        if self.__conn:
            self.__to_log('SQL Close')
            self.__conn.commit()
            self.__cur.close()
            self.__conn.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class DbLocal:
    def __init__(self):
        self.__db = sqlite3.connect('fssp.db', timeout=5)  # detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES
        self.__db.isolation_level = None  # Auto commit
        self.__c = self.__db.cursor()
        self.__c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY,
                                                 first TEXT,
                                                 name TEXT,
                                                 second TEXT,
                                                 dr DATE,
                                                 c_sum CHAR(32))''')
        # SELECT time AS "time [TIMESTAMP]" FROM u_visits
        self.__c.execute('''CREATE TABLE IF NOT EXISTS visits (time TIMESTAMP,
                                                u_id INTEGER REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
                                                adr TEXT,
                                                court INTEGER,
                                                registry TEXT,
                                                comment TEXT,
                                                jail TEXT)''')
        self.__c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS visits_IDX ON visits (time, u_id)''')
        self.__c.execute('''CREATE TABLE IF NOT EXISTS sums (
                                                u_id INTEGER REFERENCES users(id) ON UPDATE CASCADE ON DELETE CASCADE,
                                                up_date DATE,
                                                sum REAL)''')
        self.__c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS sums_IDX ON sums (u_id, up_date)''')

        self.table = {}
        self.__u_sums_get()

    @property  # DELETE THIS def
    def schema(self):
        """ To show all tables """
        self.__c.execute('SELECT * FROM sqlite_master')  # like .schema
        print(self.__c.fetchall())
        return self.__c.fetchall()

    @property
    def table(self):
        """ Return visits (to insert in other class like tk.treeview) """
        return self.__table

    @table.setter
    def table(self, conditions):
        """ Create select using conditions and the set self.__table """
        uniq = conditions.pop('uniq', False)
        c_sum = conditions.pop('c_sum', False)
        date_start = conditions.pop('start', False)
        date_end = conditions.pop('end', False)

        time = 'min(v.time)' if uniq else 'v.time'
        first = f'''SELECT u."first", u.name, u.second, u.dr, {time}, v.adr, v.court, v.registry, u.c_sum,
                            v.comment, v.jail, (SELECT sum FROM (SELECT sum, MIN(ABS(strftime('%s',v.time) -
                                                        strftime('%s', up_date))) AS xx FROM sums WHERE u_id = v.u_id))
                            FROM visits AS v 
                            LEFT JOIN users AS u ON u.id=v.u_id '''
        last = 'ORDER BY v.time DESC'
        last = 'GROUP BY u.id ' + last if uniq else last
        where = 'WHERE '  # len = 6
        if c_sum:
            where += f"u.c_sum = '{c_sum}' "
        if date_start:
            if c_sum:
                where += 'AND '
            where += 'v.time '
            where += f"BETWEEN '{date_start}' AND '{date_end}' " if date_end else f"> '{date_start}' "
        elif date_end:
            if c_sum:
                where += 'AND '
            where += f"v.time < '{date_end}' "
        if c_sum or date_start or date_end:
            first += where
        self.__table = self.__c.execute(first + last).fetchall()

    @property
    def visits(self):
        """ Return tuple: (Count visits, count users, count fssp, money to return, last visit date) """
        info = self.__c.execute('''SELECT SUM(vists), COUNT(*), SUM(fssp), sum(nearest) FROM (
                                SELECT MIN(v.time), COUNT(*) AS vists, v.registry='ФССП' AS fssp,
                                (SELECT sum FROM (SELECT sum, MIN(ABS(strftime('%s',v.time) - strftime('%s', up_date)))
                                                  FROM sums	WHERE u_id = v.u_id)) AS "nearest"
                                FROM visits AS v 
                                LEFT JOIN users AS u ON u.id=v.u_id 
                                GROUP BY u.id)''').fetchone()
        info += self.__c.execute('''SELECT MAX(time) FROM visits''').fetchone()
        return info

    @visits.setter
    def visits(self, array):
        """ Input array: F, I, O, dr, control sum, time, adr, court, registry
            Check if user or visit(time and u_id) exist then add user or\and visit
        """
        if array and isinstance(array, list):
            for row in array:
                if len(row) == 9:
                    if row[4] in self.__u_sums:
                        self.__c.execute(f"SELECT id FROM users WHERE c_sum='{row[4]}'")
                        last_id = self.__c.fetchone()[0]
                    else:
                        print('ADD USER', *row[:5])
                        self.__c.execute("INSERT INTO users(first, name, second, dr, c_sum) VALUES (?, ?, ?, ?, ?)",
                                         (row[0].upper(), row[1].upper(), row[2].upper(), row[3], row[4]))
                        last_id = self.__c.lastrowid
                        self.__u_sums_get()  # After adding - update u_sums
                    self.__c.execute("SELECT time, u_id FROM visits WHERE time=? AND u_id=?", (row[5], last_id))
                    if len(self.__c.fetchall()) > 0:
                        # print('THIS VISIT ALREADY EXIST')
                        pass
                    else:
                        self.__c.execute('''INSERT INTO visits (time, u_id, adr, court, registry) VALUES (?, ?, ?, ?, ?)''',
                                         (row[5], last_id, row[6], row[7], row[8]))

    @property
    def data(self):
        """ Return array with users to refresh data (to get sums from fssp.ru) """
        last_update = self.__c.execute('''SELECT MAX(DATE(up_date,'+1 day')) FROM sums''').fetchone()[0]
        last_update = last_update if last_update else 0  # Cos return None if no updates before
        self.__c.execute(f'''SELECT u."first", u.name, u."second", u.dr, v.time FROM visits AS v LEFT JOIN users 
                            AS u ON u.id=v.u_id WHERE v.time > '{last_update}' GROUP BY u.id''')
        return self.__c.fetchall()

    @data.setter
    def data(self, data):  # data = Tuple(column, F, I, O, dr, time, data)
        """ Update comment or jail for row or update/insert sum. For sum: time must be date format """
        u_id = self.__c.execute('''SELECT id FROM users WHERE "first"=? AND name=? AND "second"=? AND dr=?''',
                                (data[1].upper(), data[2].upper(), data[3].upper(), data[4].upper())).fetchone()
        if u_id:
            if data[0] == 'comment':
                self.__c.execute("UPDATE visits SET comment=? WHERE time=? AND u_id=?", (data[6], data[5], *u_id))
            elif data[0] == 'jail':
                self.__c.execute("UPDATE visits SET jail=? WHERE time=? AND u_id=?", (data[6], data[5], *u_id))
            elif data[0] == 'sum':
                self.__c.execute("UPDATE sums SET sum=? WHERE up_date=? AND u_id=?", (data[6], data[5], *u_id))
                if self.__c.rowcount == 0:
                    self.__c.execute("INSERT INTO sums(u_id, up_date, sum) VALUES (?, ?, ?)", (*u_id, data[5], data[6]))
            else:
                print('Wrong data. Use tuple with format: (Column Name, F, I, O, dr, Time, Data to insert)')
        else:
            print('User not fount', data[1:5])

    def __u_sums_get(self):
        """ Get array of control sums """
        self.__c.execute('''SELECT c_sum FROM users''')
        self.__u_sums = [x[0] for x in self.__c.fetchall()]


if __name__ == '__main__':
    app = DbLocal()
    app.visits = [('lebedev', 'artem', 'mudakovich', '1984-09-30', 'd4afs3j5fhz3a5d57sdf481ay7fa1k3b',
                   '2019-08-01 14:26:58', 'Moscow St. 1945 112', 353, 'ФССП'),
                  ('lebedev', 'artem', 'mudakovich', '1984-09-30', 'd4afs3j5fhz3a5d57sdf481ay7fa1k3b',
                   '2019-08-12 14:26:58', 'Moscow St. 1945 112', 353, 'ФССП'),
                  ('petrov', 'vasiliy', 'alexeevich', '1934-02-06', 'g4a7s4a5zgz6a53ads8f411ay5fa6kjp',
                   '2019-08-03 22:11:33', 'Moscow St. Serbskaya 2', 123, 'ФССП'),
                  ('petrov', 'vasiliy', 'alexeevich', '1934-02-06', 'g4a7s4a5zgz6a53ads8f411ay5fa6kjp',
                   '2019-08-04 13:02:19', 'Moscow St. Serbskaya 2', 123, 'ФССП'),
                  ('vershov', 'ilya', 'vitalevich', '1992-10-10', 'z6s2a60kg6v6j9d4shj15h1af5fs68j1',
                   '2019-08-05 08:32:44', 'Moscow St. Mendeleev 22', 123, 'ФССП'),
                  ('kuznecova', 'irina', 'anatolevna', '1989-08-30', '53ads3j5fhz3z5357sdf48sa07fa9kaz',
                   '2019-08-06 10:12:08', 'Moscow St. Sadovaya 45', 153, 'МВД'),
                  ('kuznecova', 'irina', 'anatolevna', '1989-08-30', '53ads3j5fhz3z5357sdf48sa07fa9kaz',
                   '2019-08-25 20:02:20', 'Moscow St. Sadovaya 45', 153, 'МВД')]
    app.data = ('sum', 'lebedev', 'artem', 'mudakovich', '1984-09-30', '2019-08-02', 8367.54)
    app.data = ('sum', 'petrov', 'vasiliy', 'alexeevich', '1934-02-06', '2019-08-02', 20000.01)
    app.data = ('sum', 'petrov', 'vasiliy', 'alexeevich', '1934-02-06', '2019-08-06', 35000.01)
    app.data = ('sum', 'vershov', 'ilya', 'vitalevich', '1992-10-10', '2019-08-02', 2500.22)
    app.data = ('jail', 'lebedev', 'artem', 'mudakovich', '1984-09-30', '2019-08-12 14:26:58', 'ЗАДЕРЖАН')
    app.data = ('jail', 'vershov', 'ilya', 'vitalevich', '1992-10-10', '2019-08-05 08:32:44', 'ЗАДЕРЖАН')

    app.data = ('comment', 'vershov', 'ilya', 'vitalevich', '1992-10-10', '2019-08-05 08:32:44', 'Сообщили ФССП')

    print('=== NO FILTER =================================')
    [print(x) for x in app.table]
    print('=== UNIQ, BEFORE 2019-08-04 ===================')
    app.table = {'uniq': 'X', 'end': '2019-08-04'}
    [print(x) for x in app.table]
    print('=== FILTER BY USER AND DATE 03 - 07 ===========')
    app.table = {'c_sum': 'z6s2a60kg6v6j9d4shj15h1af5fs68j1', 'start': '2019-08-03', 'end': '2019-08-07'}
    [print(x) for x in app.table]
    print('=== INFO ======================================')
    names = ('All visits', 'Users(uniq visits)', 'FSSP users', 'Uniq users pay', 'Last visit date:')
    visits = app.visits
    [print(names[i].ljust(20), visits[i]) for i in range(len(visits))]
    print('=== USERS TO CHECK ============================')
    [print(x) for x in app.data]
