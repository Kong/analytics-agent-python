import sqlite3
import tempfile
import ujson

from os.path import join

SQL_FILE = join(tempfile.gettempdir(), 'galileo.db')
initialized = False

SQL_CREATE_TABLE = 'CREATE TABLE IF NOT EXISTS alfs (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, alf TEXT)'
SQL_INSERT = 'INSERT INTO alfs (alf) VALUES (?)'
SQL_COUNT = 'SELECT COUNT(1) FROM alfs'
SQL_TRUNCATE = 'DELETE FROM alfs; VACUUM;'

class open_client(object):
    def __init__(self):
      self.connection = sqlite3.connect(SQL_FILE)

    def __enter__(self):
      self.cursor = self.connection.cursor()
      return self.cursor, self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
      self.connection.close()

class Storage(object):
  def __init__(self):
    self._execute_(SQL_CREATE_TABLE)

  def _execute_(self, query, params=[]):
    with open_client() as (client, connection):
      client.execute(query, params)
      connection.commit()

  def _fetch_one_(self, query, params=[]):
    with open_client() as (client, connection):
      client.execute(query, params)
      return client.fetchone()

  def put(self, alf):
    self._execute_(SQL_INSERT, (ujson.dumps(alf),))

  def get_batch_and_delete(self, size):
    pass

  def count(self):
    return self._fetch_one_(SQL_COUNT)[0]

  def reset(self):
    with open_client() as (client, connection):
      client.executescript(SQL_TRUNCATE)
      connection.commit()
