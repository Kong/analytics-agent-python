import time
import ujson

from unittest import TestCase, skip
from multiprocessing.managers import SyncManager
from requests.exceptions import ReadTimeout

from galileo_daemon.transport import HttpTransport
from mashape_analytics.alf import Alf
from test.helpers import http_server, mock_server

transport = HttpTransport('localhost', 12345, 2)

class TransportTest(TestCase):
  def setUp(self):
    # print 'start new daemon'
    # daemon_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'galileo_daemon', 'daemon.py'))
    # print daemon_path
    # pargs = [
    #   'python', daemon_path,
    #   '--port', str(daemon_port),
    #   '--galileo_host', host,
    #   '--galileo_port', str(port),
    #   '--queue_size', str(queue_size),
    #   '--flush_timeout', str(flush_timeout),
    #   '--connection_timeout', str(connection_timeout),
    #   '--retry_count', str(retry_count),
    # ]
    # print pargs
    # self.daemon_process = subprocess.Popen(pargs) # start a detached process

    # class QueueManager(SyncManager): pass
    # QueueManager.register('get_queue')
    # manager = QueueManager(address=('', self.daemon_port), authkey='galileo')
    # manager.connect()
    # manager.get_queue().put_nowait(obj)
    pass

  def tearDown(self):
    pass
    # self.daemon_process.terminate()
    # self.daemon_process.join()

  def test_should_send_alf(self):
    alf = Alf('service-token', 'environment', [{'entry': 1}])

    status = '200 OK' # HTTP Status
    headers = [('Content-type', 'application/json')] # HTTP Headers

    with mock_server(12345, status, headers, 'Yo!') as requests:
      transport.send([alf])

      request = requests.get()
      expectedUrl = u'http://localhost:12345/1.1.0/batch'
      expectedJson = ujson.dumps([{'version': '1.1.0', 'serviceToken': 'service-token', 'environment': 'environment', 'har': {'log': {'creator': {'name': 'mashape-analytics-agent-python', 'version': '3.0.0'}, 'entries': [{'entry': 1}]}}}])

      self.assertEqual(expectedUrl, request.get('url'))
      self.assertEqual(expectedJson, request.get('body'))

  def test_should_timeout(self):
    def handler(environ, start_response):
      # sleep for 3 seconds
      time.sleep(3)

      # proceed with normal server behaviour
      status = '200 OK'
      headers = [('Content-type', 'text/plain')]

      start_response(status, headers)
      return ['Should timeout before this response']

    with http_server(12345, handler) as requests:
      alf = Alf('service-token', 'environment', [{'entry': 1}])
      try:
        last_time = time.time()
        transport.send([alf])
        assert False
      except ReadTimeout:
        delta_time = time.time() - last_time
        self.assertGreater(delta_time, 2) # timeout should be 2s
