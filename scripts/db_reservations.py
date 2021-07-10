import sqlite3 as sq
import os.path
import gc

class Reservations():
    '''
    Database object for easy handling
    '''

    def __init__(self, database):
        self.path = os.path.abspath(database)
        self.con = sq.connect(self.path)
        self.cur = self.con.cursor()


    def fetchall(self):
        res = self.cur.execute("""SELECT week, dates.date, hour, rooma, roomb, roomc
                                  FROM dates, hours
                                  WHERE dates.date=hours.date
                                  ORDER BY julian, hour""")
        res = res.fetchall()

        #Turn the result into an easily-iterable list
        # week: hour: date: room1
        #                   room2
        #                   room3
        #             date: room1
        #                   room2
        #                   room3
        #             date
        #             date
        #             date
        #       hour: date
        #             date
        #             ....

        ret = [[week[0], []] for week in res[::40]]
        for week in ret:
            week[1] = [[hour,[]] for hour in range(1,9)]
        for i, week in enumerate(ret):
            dates = res[i*40:(i+1)*40:8]
            for hour in week[1]:
                hour[1] = [[date[1], []] for date in dates]
        for i, week in enumerate(ret):
            for hour in week[1]:
                for n, date in enumerate(hour[1]):
                    line = res[(i * 40) + hour[0] + (n * 8) - 1]
                    date[1] = [line[3],line[4],line[5]]
        return ret


    def update(self, form):
        #Insert new data, if it errors, don't commit
        try:
            self.cur.execute("DELETE FROM hours;")

            self.cur.executemany("""INSERT INTO hours
                                        ('date','hour','rooma','roomb','roomc')
                                    VALUES
                                        (?,?,?,?,?)""", form)
            self.con.commit()
            self.close()
        except Exception as e:
            self.close()
            return "An error has occurred: {}".format(e)


    def close(self):
        self.cur.close()
        self.con.close()
        gc.collect()
        return 0
