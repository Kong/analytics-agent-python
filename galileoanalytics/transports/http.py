from time import sleep
from threading import Thread, Lock
import itertools

from six.moves.urllib import urllib2
from time import time as now

from .base import BaseTransport

class HttpTransport(BaseTransport, Thread):

  def __init__(self, host):
    super(HttpTransport, self).__init__(host)

    self.lock = Lock()
    self.batch_size = 10
    # self.polling_interval = 0.25  # in seconds
    self.batch_interval = 1   # in seconds
    self.batch = []

    self.start()

  def disconnect(self):
    super(HttpTransport, self).disconnect()
    self.running = False

  def send(self):
    current_batch.append(alf)

    if len(current_batch) > self.batch_size:
      self.flush()

  def run(self):
    last_time = now()

    while self.running
      if (now() - last_time) >= self.batch_interval # or len(self.batch) > self.batch_size:
        self.flush()
      # sleep(self.polling_interval)
      sleep(self.batch_interval)

  def flush(self):
    '''
      Flush (atomic)
    '''
    if len(self.batch) > 0:
      self.lock.aquire()
      try:
        req = urllib2.Request(self.host)
        current_batch = []
      finally:
        self.lock.release()
