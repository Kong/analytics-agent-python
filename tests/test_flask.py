import time
import ujson

from unittest import TestCase
from flask import Flask

from mashapeanalytics.middleware import FlaskMiddleware
from tests.helpers import mock_server

##
# Flask App
##
def create_app():
  app = Flask('test')

  @app.route('/get')
  def show_get():
    time.sleep(0.1)  # Sleep for 10 ms
    return 'Hello World'

  @app.route('/post', methods=['POST'])
  def show_post():
    time.sleep(0.1)  # Sleep for 10 ms
    return 'Hello World'

  return app

##
# Test Flask middleware
##
class FlaskMiddewareTest(TestCase):
  def setUp(self):
    self.app = create_app()
    self.app.wsgi_app = FlaskMiddleware(self.app.wsgi_app, 'SERVICE-TOKEN', 'ENVIRONMENT', 'localhost', 56000)

    self.client = self.app.test_client()

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
      recv = self.client.get('/get?foo=bar', headers={'CONTENT_TYPE': 'text/plain', 'X-Custom': 'custom'})

      self.assertIn('200 OK', recv.status)
      self.assertIn('Hello', str(recv.data))

      request = collector.get()
      self.assertEqual(request.get('url'), u'http://localhost:56000/1.0.0/single')

      alf = ujson.loads(request.get('body'))
      self.assertTrue(alf['har']['log']['entries'][0]['timings']['wait'] >= 10)

  def test_post(self):
    status = '200 OK' # HTTP Status
    headers = [('Content-type', 'application/json')] # HTTP Headers

    # Mock collector
    with mock_server(56000, status, headers, 'Yo!') as collector:
      recv = self.client.post('/post', data='post data')

      self.assertIn('200 OK', recv.status)
      self.assertIn('Hello', str(recv.data))

      request = collector.get()
      self.assertEqual(request.get('url'), u'http://localhost:56000/1.0.0/single')
      alf = ujson.loads(request.get('body'))

      self.assertTrue(alf['har']['log']['entries'][0]['timings']['wait'] >= 10)
