import sqlite3
import os

from . import util

class User():
    def __init__(self):
        self.con = sqlite3.connect(os.path.abspath('databases/users.db'))
        self.cur = self.con.cursor()


    def _check_name_exists(self, username, shouldClose=0):
        names = self.cur.execute("""SELECT name FROM users""").fetchall()
        names = [name[0] for name in names]

        if username in names:
            return True
        elif shouldClose:
            self._close()
        return False


    def validate(self, username, password):
        assert self._check_name_exists(username, shouldClose=1)

        truePassword, salt, admin = self.cur.execute("""SELECT pswd, salt, admin FROM users WHERE name=?""", (username,)).fetchone()
        password = util.hash_password(password, salt)

        if password == truePassword:
            self._close()
            return admin
        else:
            self._close()
            assert False


    def new(self, username, password, isAdmin):
        #We assume the password has been crosschecked

        assert not self._check_name_exists(username)
        if password == '':
            return 'Password cannot be empty'
        salt = util.get_salt()
        password = util.hash_password(password, salt)

        try:
            self.cur.execute("""INSERT INTO users (name, pswd, salt, admin)
                                VALUES (?,?,?,?)""", (username, password, salt, isAdmin))
            self.con.commit()
            self._close()
        except Exception as e:
            return "An error has occurred when trying to add user: {}".format(e)


    def remove(self, username):
        try:
            self.cur.execute("""DELETE FROM users WHERE name=(?)""", (username,))
            self.con.commit()
        except Exception as e:
            self._close()
            return "An error has occurred when trying to remove user: {}".format(e)
        self._close()


    def list_all(self):
        res = self.cur.execute("""SELECT name FROM users""").fetchall()
        users = [r[0] for r in res]
        return users

    def _close(self):
        self.cur.close()
        self.con.close()
