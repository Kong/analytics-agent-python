import time
import ujson

from unittest import TestCase

from multiprocessing import Process
from six.moves.urllib.request import urlopen
from werkzeug.test import Client
from wsgiref.simple_server import make_server

from mashapeanalytics.middleware import WsgiMiddleware
from tests.helpers import host, mock_server

##
# Wsgi App
##
def create_app():
  def app(env, start_response):
    time.sleep(0.01)  # Sleep for 10 ms
    start_response('200 OK CUSTOM', [('Content-Type','text/plain')])
    return ['Hello World']

  return app

##
# Test WSGI middleware
##
class WsgiMiddewareTest(TestCase):
  def setUp(self):
    self.app = WsgiMiddleware(create_app(), 'SERVICE-TOKEN', 'ENVIRONMENT', 'localhost', 56000)

  def tearDown(self):
    pass

  @property
  def middleware(self):
    return self._middleware

  def test_get(self):
    status = '200 OK' # HTTP Status
    headers = [('Content-type', 'application/json')] # HTTP Headers

    # Mock collector
    with mock_server(56000, status, headers, 'Yo!') as collector:
      client = Client(self.app)
      data, status, headers = client.open()
      data = ''.join(data)
      self.assertIn('Hello', data)

      request = collector.get()
      self.assertEqual(request.get('url'), u'http://localhost:56000/1.0.0/single')

      alf = ujson.loads(request.get('body'))
      self.assertEqual(alf['serviceToken'], 'SERVICE-TOKEN')
      self.assertEqual(alf['har']['log']['creator']['name'], 'mashape-analytics-agent-python')
      self.assertEqual(alf['har']['log']['entries'][0]['request']['method'], 'GET')
      self.assertEqual(alf['har']['log']['entries'][0]['request']['url'], 'http://localhost/')
      self.assertEqual(alf['har']['log']['entries'][0]['response']['status'], 200)
      self.assertEqual(alf['har']['log']['entries'][0]['response']['statusText'], 'OK CUSTOM')
      self.assertEqual(alf['har']['log']['entries'][0]['response']['content']['mimeType'], 'text/plain')
      self.assertEqual(alf['har']['log']['entries'][0]['response']['content']['size'], 11)
      self.assertTrue(alf['har']['log']['entries'][0]['timings']['wait'] >= 10)
