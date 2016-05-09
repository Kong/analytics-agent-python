import os
import sys
import time
import datetime

from argparse import ArgumentParser
from multiprocessing.managers import SyncManager
from multiprocessing import Process, Queue, TimeoutError
from threading import Timer, Thread, Event

from mashape_analytics.storage import Storage
from transport import HttpTransport

import multiprocessing, logging
logger = multiprocessing.log_to_stderr()
logger.setLevel(logging.INFO)

store = Storage()

class KeepAliveThread(Thread):
  '''keep daemon lock alive'''
  def __init__(self, threadID, pid, flush_timeout):
    Thread.__init__(self)
    self._stop = Event()
    self.threadID = threadID
    self.name = 'keep-alive'
    self.pid = pid
    self.flush_timeout = flush_timeout

  def stop(self):
    self._stop.set()

  @property
  def stopped(self):
    return self._stop.isSet()

  def run(self):
    print 'keep-alive', self.pid
    while not self.stopped:
      store.put_daemon_row(self.pid, datetime.datetime.now() + datetime.timedelta(seconds=self.flush_timeout + 1))
      time.sleep(self.flush_timeout)

class AlfConsumerThread(Thread):
  '''keep daemon lock alive'''
  def __init__(self, threadID, queue, host, port, queue_size, flush_timeout, connection_timeout, retry_count):
    Thread.__init__(self)
    self._stop = Event()
    self.threadID = threadID
    self.name = 'alf-consumer'
    self.transport = HttpTransport(host, port, connection_timeout, retry_count)
    self.queue = queue
    self.queue_size = queue_size
    self.flush_timeout = flush_timeout

  def stop(self):
    self._stop.set()

  @property
  def stopped(self):
    return self._stop.isSet()

  def flush(self):
    print 'flushing'
    rows = store.get_then_delete(self.queue_size)
    objs = [row[1] for row in rows]

    try:
      self.transport.send(objs)
    except:
      pass
      # TODO log failure
      # TODO alternatively, on connection error or timeout, add alfs back in for retry
      # self.put_all(objs)

  def run(self):
    running_count = store.count()
    timer = None

    while not self.stopped:
      print 'waiting for alf'
      try:
        alf = self.queue.get(timeout=self.flush_timeout)
      except TimeoutError:
        continue

      if alf == 'exit':
        self.stop()
        continue

      print 'got alf'

      store.put(dict(alf))
      running_count += 1

      if running_count >= self.queue_size:
        running_count = 0
        if timer:
          timer.cancel()
        self.flush()

      if not timer:
        timer = Timer(self.flush_timeout, flush)
        timer.start()

def create_server(queue, port=8525):
  class QueueManager(SyncManager): pass
  QueueManager.register('get_queue', callable=lambda: queue)
  manager = QueueManager(address=('', port), authkey='galileo')

  return manager

if __name__ == '__main__':
  print 'daemon', os.getpid()
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
      print daemon_row
      print 'daemon already running'
      exit()  # process already running


  queue = Queue()

  # create threads
  keep_alive = KeepAliveThread(1, os.getpid(), args.flush_timeout)
  alf_consumer = AlfConsumerThread(2, queue, args.galileo_host, args.galileo_port, args.queue_size, args.flush_timeout, args.connection_timeout, args.retry_count)

  # start the threads
  keep_alive.start()
  alf_consumer.start()

  print 'starting daemon server'
  # run queue manager
  server = create_server(queue, args.port)
  server.start()

  # close everything
  print 'close up'
  alf_consumer.join()
  keep_alive.join()

  server.terminate()
  server.join()
  server.shutdown()
