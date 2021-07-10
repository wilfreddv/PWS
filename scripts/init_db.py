'''
Initial creation of the DB, run once only!
'''

from getpass import getpass
import util
import re
import sqlite3 as sq3
import os
import datetime

from config import WEEKS_AHEAD

###RESERVATIONS###
def create_table_reservations(con, cur):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS dates (
        date    TEXT PRIMARY KEY,
        week    INTEGER,
        day     INTEGER,
        julian  REAL
        )''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS hours (
        date    TEXT,
        hour    INTEGER,
        rooma   TEXT DEFAULT '',
        roomb   TEXT DEFAULT '',
        roomc   TEXT DEFAULT '',
        PRIMARY KEY (date, hour),
        FOREIGN KEY (date) REFERENCES dates (date)
        )''')

    con.commit()


def insert_template(con, cur):
    wy = datetime.datetime.now().strftime("%W %Y").split(' ')
    week = wy[0]
    year = wy[1]

    #Inserts all weeks from current week to WEEKS_AHEAD weeks from now
    for i in range(0, WEEKS_AHEAD):
        nextweek = int(week) + i
        #If the weeknumber > 52, it means it is a new year
        if nextweek > 53:
            nextweek -= 52
            year = int(wy[1]) + 1

        insert_week(str(nextweek), str(year), con, cur)


def insert_week(week, year, con, cur):
    #Outer loop creates 5 days
    #Inner loop creates 8 (or 7) hours for every day
    for daynr in range(1, 6):
        #Calc date
        yeardate = str(datetime.datetime.strptime("{}-{}-{}".format(year, week, daynr),	#Spits out a list:
                        "%Y-%W-%w")).split(' ')[0]		#['yyyy-mm-dd']
        ymd = yeardate.split('-')
        date = "{}/{}".format(ymd[2], ymd[1])	#Creates date in string form: 'dd/mm'

        cur.execute('''
            INSERT INTO dates (date, week, day, julian)
            VALUES (?, ?, ?, julianday(?))''',
            (date, week, daynr, yeardate))


    con.commit()


def make_reservations(cwd):
    path = os.path.join(cwd, '../databases/reservations.db')
    try:
        if not os.path.isfile(path):
            con = sq3.connect(path)
            cur = con.cursor()

            create_table_reservations(con, cur)
            insert_template(con, cur)
            cur.close()
            con.close()

            print('Successfully created database!')
        else:
            print('Database already exists...')
    except Exception as e:
        print("An exception has occurred: {}".format(e))
        os.remove(path)


###USERS###
def create_table_users(con, cur):
    cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                name    CHAR(3) PRIMARY KEY,
                pswd    CHAR,
                salt    BLOB,
                admin   INT)
                ''')
    con.commit()


def insert_user(name="",password="",salt="",admin=0,con=None,cur=None):
    cur.execute('''
                INSERT INTO users (name, pswd, salt, admin)
                VALUES (?,?,?,?)
                ''', (name, password, salt, admin))
    con.commit()


def make_users(cwd):
    path = os.path.join(cwd, '../databases/users.db')
    try:
        if not os.path.isfile(path):
            con = sq3.connect(path)
            cur = con.cursor()

            create_table_users(con, cur)

            name = input("Voer de naam van de administrator in: ")
            while not re.fullmatch(r'[A-Z]{3}',name):
                print("Gebruikersnaam moet uit 3 hoofdletters bestaan")
                name = input("Voer de naam van de administrator in: ")

            pasw =  getpass("Voer een wachtwoord in: ")
            pasc =  getpass("Voer het wachtwoord nogmaals in: ")

            while pasw != pasc:
                print("De wachtwoorden komen niet overeen!")

                pasw =  getpass("Voer een wachtwoord in: ")
                pasc =  getpass("Voer het wachtwoord nogmaals in: ")


            salt = util.get_salt()
            password = util.hash_password(pasw, salt)
            del pasw
            del pasc

            insert_user(name=name, password=password, salt=salt, admin=1, con=con, cur=cur)

            cur.close()
            con.close()

            print("Successfully created database")
        else:
            print("The database already exists")

    except Exception as e:
        print("An exception has occurred: {}".format(e))
        os.remove(path)


if __name__ == '__main__':
    cwd = os.path.dirname(__file__)

    if not os.path.isdir(os.path.join(cwd, '../databases')):
        os.mkdir(os.path.join(cwd, '../databases'))
    make_reservations(cwd)
    make_users(cwd)
