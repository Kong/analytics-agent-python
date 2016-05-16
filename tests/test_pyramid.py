import time
import ujson

from unittest import TestCase
from pyramid.config import Configurator
from pyramid.response import Response
from werkzeug.test import Client

from mashapeanalytics.middleware import WsgiMiddleware
from tests.helpers import mock_server

##
# Pyramid App
##
def create_app():
  def root(request):
    time.sleep(0.01)  # Sleep for 10 ms
    return Response('Hello World')

  config = Configurator()
  config.add_route('root', '/')
  config.add_view(root, route_name='root')

  app = config.make_wsgi_app()

  return app

##
# Test Pyramid
##
class PyramidMiddewareTest(TestCase):
  def setUp(self):
    self.app = WsgiMiddleware(create_app(), 'SERVICE_TOKEN', 'ENVIRONMENT', 'localhost', 56000)

  def tearDown(self):
    pass

  def test_get(self):
    status = '200 OK' # HTTP Status
    headers = [('Content-type', 'application/json')] # HTTP Headers

    # Mock collector
    with mock_server(56000, status, headers, 'Yo!') as collector:
      client = Client(self.app)
      data, status, headers = client.open()
      data = (b'').join(data)

      self.assertIn('Hello', str(data))

      request = collector.get()
      self.assertEqual(request.get('url'), u'http://localhost:56000/1.0.0/single')

      alf = ujson.loads(request.get('body'))
      self.assertTrue(alf['har']['log']['entries'][0]['timings']['wait'] >= 10)
