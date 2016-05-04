import subprocess
import os

from multiprocessing.managers import SyncManager

from storage import Storage


class Analytics(object):
  def __init__(self, host, port, queue_size, flush_timeout, connection_timeout, retry_count):
    self.store = Storage()

    daemon_row = self.store.get_daemon_row()
    expires = time.mktime(daemon_row[1].timetuple()) if daemon_row else time.time() - 1

    if time.time() > expires:
      daemon_path = os.path.join(dirname(__file__), 'galileo_daemon', 'daemon.py')
      pargs = [
        'python', daemon_path,
        '--galileo_host', host,
        '--galileo_port', port,
        '--queue_size', queue_size,
        '--flush_timeout', flush_timeout,
        '--connection_timeout', connection_timeout,
        '--retry_count', retry_count,
      ]
      p = subprocess.Popen(pargs) # start a detached process

    class QueueManager(SyncManager): pass
    QueueManager.register('get_queue')
    manager = QueueManager(address=('', 8525), authKey='galileo')
    manager.connect()
    self.queue = manager.get_queue()

  def submit(self, alf):
    self.queue.put(dict(alf))
