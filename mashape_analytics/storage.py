import sqlite3
import tempfile
import ujson
import time

from os.path import join

SQL_FILE = join(tempfile.gettempdir(), 'galileo.db')
initialized = False

SQL_CREATE_TABLE = 'CREATE TABLE IF NOT EXISTS queue (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, json TEXT)'
SQL_CREATE_INDEX = 'CREATE INDEX IF NOT EXISTS ix_queue_created_at ON queue (created_at ASC)'
SQL_INSERT = 'INSERT INTO queue (json) VALUES (?)'
SQL_COUNT = 'SELECT COUNT(1) FROM queue'
SQL_OLDEST = 'SELECT created_at FROM queue ORDER BY created_at ASC LIMIT 1'
SQL_TRUNCATE = 'DELETE FROM queue; VACUUM;'
SQL_GET_ALFS = 'SELECT id, json FROM queue ORDER BY created_at ASC LIMIT ?'
SQL_DELETE = 'DELETE FROM queue WHERE id in (?)'

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
    with open_client() as (client, connection):
      client.execute(SQL_CREATE_TABLE)
      client.execute(SQL_CREATE_INDEX)
      connection.commit()

  def _execute_(self, query, params=[]):
    with open_client() as (client, connection):
      client.execute(query, params)
      connection.commit()

  def _fetch_one_(self, query, params=[]):
    with open_client() as (client, connection):
      client.execute(query, params)
      return client.fetchone()

  def put(self, obj):
    self._execute_(SQL_INSERT, (ujson.dumps(obj),))

  def put_all(self, objs=[]):
    with open_client() as (client, connection):
      client.executemany(SQL_INSERT, [(ujson.dumps(obj),) for obj in objs])
      connection.commit()

  def get(self, size):
    with open_client() as (client, connection):
      return [(row[0], ujson.loads(row[1])) for row in client.execute(SQL_GET_ALFS, (size,))]

  def delete(self, ids=[]):
    self._execute_(SQL_DELETE, (','.join([str(id) for id in ids]),))

  def count(self):
    return self._fetch_one_(SQL_COUNT)[0]

  def oldest_time(self):
    return time.strptime(self._fetch_one_(SQL_OLDEST)[0], '%Y-%m-%d %H:%M:%S')

  def reset(self):
    with open_client() as (client, connection):
      client.executescript(SQL_TRUNCATE)
      connection.commit()
