import logging
import sqlite3

logger = logging.getLogger(__name__)


class DBHelper(object):
    def __init__(self, name=None):
        self.con = None
        self.cur = None
        if name:
            self.open(name)

    def open(self, name):
        try:
            self.con = sqlite3.connect(name)
            self.cur = self.con.cursor()
        except sqlite3.Error as e:
            logger.error('Error connecting to database!')
            logger.error(e)

    def commit(self):
        if self.con:
            self.con.commit()

    def close(self):
        if self.con:
            self.con.commit()
            self.cur.close()
            self.con.close()

    def query(self, sql, args=(), one=False):
        self.cur.execute(sql, args)
        rv = [dict((self.cur.description[idx][0], value)
                   for idx, value in enumerate(row)) for row in self.cur.fetchall()]
        return (rv[0] if rv else None) if one else rv

    def execute(self, sql, args=()):
        self.cur.execute(sql, args)
