import os
import time
import ujson
import subprocess

from unittest import TestCase, skip
from multiprocessing.managers import SyncManager

from mashape_analytics.storage import Storage

store = Storage()

class DaemonTest(TestCase):
  def setUp(self):
    print store.get_daemon_row()
    store.reset()
    print 'start new daemon'
    daemon_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'galileo_daemon', 'daemon.py'))
    print daemon_path
    pargs = [
      'python', daemon_path,
      '--port', '8525',
      '--galileo_host', 'localhost',
      '--galileo_port', '12345',
      '--queue_size', '1000',
      '--flush_timeout', '2',
      '--connection_timeout', '2',
      '--retry_count', '0',
    ]
    print pargs
    self.daemon_process = subprocess.Popen(pargs) # start a detached process
    print 'started daemon'
    time.sleep(1)
    print store.get_daemon_row()

  def tearDown(self):
    print 'teardown'
    manager = self.connect_to_manager()
    queue = manager.get_queue()
    queue.put('exit')
    # self.manager.shutdown()
    self.daemon_process.terminate()
    print 'daemon process terminated'
    pass

  def connect_to_manager(self):
    class QueueManager(SyncManager): pass
    QueueManager.register('get_queue')
    manager = QueueManager(address=('', 8525), authkey='galileo')
    print 'connecting'
    manager.connect()
    print 'connected'
    return manager

  @skip('')
  def test_should_quit_daemon(self):
    manager = self.connect_to_manager()
    print 'started'
