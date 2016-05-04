import os
import time
import datetime

from argparse import ArgumentParser
from multiprocessing.managers import SyncManager
from multiprocessing import Process, Queue
from threading import Timer

from mashape_analytics.storage import Storage
from transport import HttpTransport

store = Storage()

def alive(store, flush_timeout):
  '''keep daemon lock alive'''
  while True:
    store.put_daemon_row(os.getpid(), datetime.datetime.now() + datetime.timedelta(seconds=flush_timeout + 1))
    time.sleep(flush_timeout)

def consumer(queue, host, port, queue_size, flush_timeout, connection_timeout, retry_count):
  '''queue consumer'''
  transport = HttpTransport(host, port, connection_timeout, retry_count)
  running_count = store.count()
  oldest_time = store.oldest_time()

  def flush():
    rows = store.get_then_delete(queue_size)
    objs = [row[1] for row in rows]

    try:
      transport.send(objs)
    except:
      pass
      # TODO log failure
      # TODO alternatively, on connection error or timeout, add alfs back in for retry
      # self.put_all(objs)

  while True:
    alf = queue.get()

    if not oldest_time:
      oldest_time = time.time()

    store.put(dict(alf))
    running_count += 1

    if running_count >= queue_size:
      running_count = 0
      if timer:
        timer.cancel()
      flush()

    if not timer:
      timer = Timer(flush_timeout, flush)
      timer.start()


def create_server(queue, host='', port=8525):
  class QueueManager(SyncManager): pass
  QueueManager.register('get_queue', callable=lambda: queue)
  manager = QueueManager(address=(host, port), authKey='galileo')

  return manager

if __name__ == '__main__':
  # TODO pass arguments
  parser = ArgumentParser(description='Daemon process for Galileo')
  parser.add_argument('--port', type=int, default=8525)
  parser.add_argument('--galileo_host', type=str, default='collector.galileo.mashape.com')
  parser.add_argument('--galileo_port', type=int, default=443)
  parser.add_argument('--queue_size', type=int, default=1000)
  parser.add_argument('--flush_timeout', type=int, default=2)
  parser.add_argument('--connection_timeout', type=int, default=30)
  parser.add_argument('--retry_count', type=int, default=0)
  args = parser.parse_args()

  # check for existing daemon
  daemon_row = store.get_daemon_row()
  if daemon_row:
    expires = time.mktime(daemon_row[1].timetuple())
    if time.time() < expires:
      # TODO log exit
      exit()  # process already running

  # keep daemon lock alive
  keep_alive_process = Process(target=alive, args=(store, args.flush_timeout,))
  keep_alive_process.start()

  # run daemon background worker
  queue = Queue()
  p = Process(target=consumer, args=(queue, args.galileo_host, args.galileo_port, args.queue_size, args.flush_timeout, args.connection_timeout, args.retry_count,))
  p.start()

  # run queue manager
  server = create_server(queue, '', args.port)
  server.start()
  p.join()
