from multiprocessing import Process
from threading import Timer
from storage import Storage
from transport import HttpTransport

class Analytics(object):
  def __init__(self, batch_size, flush_timeout):
    self.batch_size = batch_size
    self.flush_timeout = flush_timeout
    self.timer = None
    self.store = Storage()
    # self.transport = HttpTransport()

  def submit(self, alf):
    self.running_count += 1
    self.store.put(alf)

    if not self.timer:
      self.timer = Timer(self.flush_timeout, self.flush)

    if self.store.count() >= self.batch_size:
      self.timer.cancel()
      self.flush()

  def flush(self):
    # TODO get alfs, delete from sqlite, send them
    # TODO on connection error or timeout, add alfs back in
    # rows = self.store.get(self.batch_size)
    # alf_ids = [row[0] for row in rows]
    # alfs = [row[1] for row in rows]
    # self.delete(alf_ids)
    # try:
    #   self.transport.send(alfs)
    # except:
    #   self.put_all(alfs)
