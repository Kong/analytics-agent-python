import time
import ujson

from django.conf import settings
settings.configure(
  INSTALLED_APPS=['apianalytics'],
  ALLOWED_HOSTS=['testserver'],
  MASHAPE_ANALYTICS_SERVICE_TOKEN='SERVICE-TOKEN',
  MASHAPE_ANALYTICS_ENVIRONMENT='ENVIRONMENT',
  MASHAPE_ANALYTICS_HOST='localhost',
  MASHAPE_ANALYTICS_PORT=56000
)

from unittest import TestCase
from django.test import RequestFactory
from django.http import HttpRequest, HttpResponse

from mashapeanalytics.middleware import DjangoMiddleware
from tests.helpers import mock_server

requestFactory = RequestFactory()

##
# Helper Functions
##
def createResponse(status, headers, content=''):
  response = HttpResponse(content)
  response.status_code = status

  for header in headers:
    response[header] = headers[header]

  return response


##
# Test Django middleware
##
class DjangoMiddewareTest(TestCase):
  def setUp(self):
    self._middleware = DjangoMiddleware()

  def tearDown(self):
    pass

  @property
  def middleware(self):
    return self._middleware

  def test_get(self):
    status = '200 OK' # HTTP Status
    headers = [('Content-type', 'application/json')] # HTTP Headers

    with mock_server(56000, status, headers, 'Yo!') as collector:
      req = requestFactory.get('/get?foo=bar', {'query': 'string'})
      res = createResponse(200, {
        'Content-Type': 'text/html; charset=UTF-8'
      }, 'Test Body')

      self.middleware.process_request(req)
      time.sleep(0.01)  # Sleep for 10 ms
      response = self.middleware.process_response(req, res)

      request = collector.get()
      self.assertEqual(request.get('url'), u'http://localhost:56000/1.0.0/single')
      alf = ujson.loads(request.get('body'))
      self.assertIn('text/html', response['Content-Type'])
      self.assertTrue(alf['har']['log']['entries'][0]['timings']['wait'] >= 10)

  def test_post(self):
    status = '200 OK' # HTTP Status
    headers = [('Content-type', 'application/json')] # HTTP Headers

    with mock_server(56000, status, headers, 'Yo!') as collector:
      req = requestFactory.post('/post?foo=bar', {'query': 'string'})
      res = createResponse(200, {
        'Content-Type': 'application/json'
      }, '{"foo": "bar"}')

      self.middleware.process_request(req)
      time.sleep(0.01)  # Sleep for 10 ms
      response = self.middleware.process_response(req, res)

      request = collector.get()
      self.assertEqual(request.get('url'), u'http://localhost:56000/1.0.0/single')
      alf = ujson.loads(request.get('body'))
      self.assertIn('json', response['Content-Type'])
