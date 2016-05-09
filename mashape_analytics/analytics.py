import os
import time
import subprocess

from multiprocessing.managers import SyncManager

from storage import Storage


class Analytics(object):
  def __init__(self, host, port, queue_size, flush_timeout, connection_timeout, retry_count, daemon_port=8525):
    self.store = Storage()
    self.daemon_port = daemon_port

    daemon_row = self.store.get_daemon_row()
    print daemon_row
    expires = time.mktime(daemon_row[1].timetuple()) if daemon_row else time.time() - 1

    print time.time()
    print expires
    print time.time() > expires
    if time.time() > expires:
      print 'start new daemon'
      daemon_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'galileo_daemon', 'daemon.py'))
      print daemon_path
      pargs = [
        'python', daemon_path,
        '--port', str(daemon_port),
        '--galileo_host', host,
        '--galileo_port', str(port),
        '--queue_size', str(queue_size),
        '--flush_timeout', str(flush_timeout),
        '--connection_timeout', str(connection_timeout),
        '--retry_count', str(retry_count),
      ]
      print pargs
      p = subprocess.Popen(pargs) # start a detached process

  def put_queue(self, obj):
    class QueueManager(SyncManager): pass
    QueueManager.register('get_queue')
    manager = QueueManager(address=('localhost', self.daemon_port), authkey='galileo')
    manager.connect()
    manager.get_queue().put_nowait(obj)
    manager.shutdown()

  def submit(self, alf):
    self.put_queue(dict(alf))
