from multiprocessing import Process
from threading import Timer
from storage import Storage
from transport import HttpTransport

class Analytics(object):
  def __init__(self, host, port, batch_size, flush_timeout, connection_timeout, retry_count):
    self.batch_size = batch_size
    self.flush_timeout = flush_timeout
    self.timer = None
    self.store = Storage()
    self.transport = HttpTransport(host, port, connection_timeout, retry_count)

  def submit(self, alf):
    self.running_count += 1
    self.store.put(dict(alf))

    if not self.timer:
      self.timer = Timer(self.flush, self.flush)

    if self.store.count() >= self.batch_size:
      # print 'Flushing (batch full)'
      self.timer.cancel()
      p = Process(target=self.flush)
      p.start()
      p.join()

  def flush(self):
    # get alfs, delete from sqlite, send them
    rows = self.store.get(self.batch_size)
    obj_ids = [row[0] for row in rows]
    objs = [row[1] for row in rows]
    self.delete(obj_ids)
    try:
      # print 'send'
      self.transport.send(objs)
    except:
      # on connection error or timeout, add alfs back in
      self.put_all(objs)
