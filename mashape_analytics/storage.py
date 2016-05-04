import sqlite3
import tempfile
import ujson
import time
import calendar

from os.path import join

SQL_FILE = join(tempfile.gettempdir(), 'galileo.db')
initialized = False

SQL_CREATE_QUEUE_TABLE = 'CREATE TABLE IF NOT EXISTS queue (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, json TEXT)'
SQL_CREATE_QUEUE_INDEX = 'CREATE INDEX IF NOT EXISTS ix_queue_created_at ON queue (created_at ASC)'
SQL_CREATE_DAEMON_TABLE = 'CREATE TABLE IF NOT EXISTS daemon (id INTEGER PRIMARY KEY, process_id INTEGER, expires TIMESTAMP)'

SQL_FETCH_DAEMON = 'SELECT process_id, expires from daemon LIMIT 1'
SQL_UPDATE_DAEMON = 'INSERT OR REPLACE INTO daemon (id, process_id, expires) VALUES (1, ?, ?)'
SQL_INSERT_JSON = 'INSERT INTO queue (json) VALUES (?)'
SQL_COUNT_QUEUE = 'SELECT COUNT(1) FROM queue'
SQL_OLDEST_IN_QUEUE = 'SELECT created_at FROM queue ORDER BY created_at ASC LIMIT 1'
SQL_RESET_ALL = 'DELETE FROM queue; DELETE FROM daemon; VACUUM;'
SQL_GET_ALFS = 'SELECT id, json FROM queue ORDER BY created_at ASC LIMIT ?'
SQL_DELETE_IN_QUEUE = 'DELETE FROM queue WHERE id IN ({0})'

class open_client(object):
    def __init__(self):
      self.connection = sqlite3.connect(SQL_FILE, detect_types=sqlite3.PARSE_DECLTYPES)

    def __enter__(self):
      return self.connection.cursor(), self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
      self.connection.close()

class Storage(object):
  def __init__(self):
    with open_client() as (client, connection):
      client.execute(SQL_CREATE_QUEUE_TABLE)
      client.execute(SQL_CREATE_QUEUE_INDEX)
      client.execute(SQL_CREATE_DAEMON_TABLE)
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
    self._execute_(SQL_INSERT_JSON, (ujson.dumps(obj),))

  def put_all(self, objs=[]):
    with open_client() as (client, connection):
      client.executemany(SQL_INSERT_JSON, [(ujson.dumps(obj),) for obj in objs])
      connection.commit()

  def get(self, size):
    with open_client() as (client, connection):
      return [(row[0], ujson.loads(row[1])) for row in client.execute(SQL_GET_ALFS, (size,))]

  def delete(self, ids=[]):
    self._execute_(SQL_DELETE_IN_QUEUE.format(','.join([str(id) for id in ids])))

  def get_then_delete(self, size):
    with open_client() as (client, connection):
      client.execute(SQL_GET_ALFS, (size,))
      items = client.fetchall()
      item_ids = [row[0] for row in items]
      client.execute(SQL_DELETE_IN_QUEUE.format(','.join([str(id) for id in item_ids])))
      connection.commit()

    return [(row[0], ujson.loads(row[1])) for row in items]

  def count(self):
    return self._fetch_one_(SQL_COUNT_QUEUE)[0]

  def oldest_time(self):
    '''retreive the oldest queue item'''
    row = self._fetch_one_(SQL_OLDEST_IN_QUEUE)
    return time.mktime(row[0].timetuple()) if row else 0

  def get_daemon_row(self):
    rows = self._fetch_one_(SQL_FETCH_DAEMON)
    return rows if rows and len(rows) else None

  def put_daemon_row(self, pid, expires):
    self._execute_(SQL_UPDATE_DAEMON, (pid, expires,))

  def reset(self):
    '''only use for test'''
    with open_client() as (client, connection):
      client.executescript(SQL_RESET_ALL)
      connection.commit()
