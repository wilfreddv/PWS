import sqlite3 as sq3
import datetime
import os
from config import WEEKS_AHEAD


cwd = os.path.dirname(__file__)
path = os.path.join(cwd, '../databases/reservations.db')

wy = datetime.datetime.now().strftime("%W %Y").split(' ')
week = wy[0]
year = wy[1]
last_week = str(int(week)-1)
new_week = str(int(week)+WEEKS_AHEAD-1)

con = sq3.connect(os.path.abspath(path))
cur = con.cursor()

#DELETE THE LAST WEEK
try:
    dates = cur.execute('''SELECT dates.date FROM dates WHERE week=(?);''', (last_week,)).fetchall()
    cur.executemany('''DELETE FROM hours WHERE hours.date=(?);''', dates)
    cur.execute('''DELETE FROM dates WHERE week=(?)''', (last_week,))
    con.commit()
except Exception as e:
    print(e)
    exit()

#ENTER THE NEW WEEK
for daynr in range(1, 6):
    #Calc date
    yeardate = str(datetime.datetime.strptime("{}-{}-{}".format(year, new_week, daynr),	#Spits out a list:
                    "%Y-%W-%w")).split(' ')[0]		#['yyyy-mm-dd']
    ymd = yeardate.split('-')
    date = "{}/{}".format(ymd[2], ymd[1])	#Creates date in string form: 'dd/mm'

    cur.execute('''
        INSERT INTO dates (date, week, day, julian)
        VALUES (?, ?, ?, julianday(?))''',
        (date, new_week, daynr, yeardate))


con.commit()
cur.close()
con.close()
