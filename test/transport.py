import ujson

from unittest import TestCase
from mashape_analytics.transport import HttpTransport
from mashape_analytics.alf import Alf
from test.helpers import collector

transport = HttpTransport('localhost', 12345, 30)

class TransportTest(TestCase):
  def setUp(self):
    pass

  def tearDown(self):
    pass

  def test_should_send_alf(self):
    alf = Alf('service-token', 'environment', [{'entry': 1}])

    status = '200 OK' # HTTP Status
    headers = [('Content-type', 'application/json')] # HTTP Headers

    with collector(12345, status, headers, 'Yo!') as requests:
      transport.send([alf])

      request = requests.get()
      expectedUrl = u'http://localhost:12345/1.1.0/batch'
      expectedJson = ujson.dumps([{'version': '1.1.0', 'serviceToken': 'service-token', 'environment': 'environment', 'har': {'log': {'creator': {'name': 'mashape-analytics-agent-python', 'version': '3.0.0'}, 'entries': [{'entry': 1}]}}}])

      self.assertEqual(expectedUrl, request.get('url'))
      self.assertEqual(expectedJson, request.get('body'))
