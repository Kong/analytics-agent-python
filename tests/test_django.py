import time

from unittest import TestCase
from django.test import RequestFactory
from django.http import HttpRequest, HttpResponse

from galileoanalytics import capture as Capture
from galileoanalytics.middleware import DjangoMiddleware
from tests.helpers import host, zmq_pull_once

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
    Capture.disconnect()

  @property
  def middleware(self):
    return self._middleware

  def test_get(self):
    req = requestFactory.get('/get?foo=bar', {'query': 'string'})
    res = createResponse(200, {
      'Content-Type': 'text/html; charset=UTF-8'
    }, 'Test Body')

    self.middleware.process_request(req)
    time.sleep(0.01)  # Sleep for 10 ms
    response = self.middleware.process_response(req, res)

    version, json = zmq_pull_once(host())

    self.assertEqual(version, 'alf_1.0.0')
    self.assertIn('text/html', response['Content-Type'])
    self.assertTrue(json['har']['log']['entries'][0]['timings']['wait'] >= 10)

  def test_post(self):
    req = requestFactory.post('/post?foo=bar', {'query': 'string'})
    res = createResponse(200, {
      'Content-Type': 'application/json'
    }, '{"foo": "bar"}')

    self.middleware.process_request(req)
    time.sleep(0.01)  # Sleep for 10 ms
    response = self.middleware.process_response(req, res)

    version, json = zmq_pull_once(host())

    self.assertEqual(version, 'alf_1.0.0')
    self.assertIn('json', response['Content-Type'])
