import os
import sqlite3

DATABASE_URL = os.environ.get('DATABASE_URL')


class Database(object):
    """A Database."""

    def __init__(self, db_path=None):
        # If no db_path was provided, fallback to $DATABASE_URL.
        self.db_path = db_path or DATABASE_URL

        if not self.db_path:
            raise ValueError('You must provide a db_path.')

        self._conn = sqlite3.connect(self.db_path)
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc, val, traceback):
        self.close()

    def query(self, query, args=(), one=False):
        """Executes the given SQL query against the Database."""
        self._cursor.execute(query, args)
        rv = [dict((self._cursor.description[idx][0], value)
                   for idx, value in enumerate(row)) for row in self._cursor.fetchall()]
        return (rv[0] if rv else None) if one else rv

    def execute(self, query, args=()):
        self._cursor.execute(query, args)

    def commit(self):
        self._conn.commit()

    def close(self):
        """Closes the Database."""

        self.commit()
        self._conn.close()
