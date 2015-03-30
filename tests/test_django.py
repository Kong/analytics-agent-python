import time

from unittest import TestCase
from django.test import RequestFactory
from django.http import HttpRequest, HttpResponse

from apianalytics.middleware import DjangoMiddleware
from tests.helpers import zmq_pull_once

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

  @property
  def middleware(self):
    return self._middleware

  def test_get(self):
    req = requestFactory.get('/get')
    res = createResponse(200, {
      'Content-Type': 'text/html; charset=UTF-8'
    })

    response = self.middleware.process_request(req)
    time.sleep(0.01)  # Sleep for 10 ms
    response = self.middleware.process_response(req, res)

    json = zmq_pull_once()

    # import pdb
    # pdb.set_trace()

    self.assertIn('text/html', response['Content-Type'])
    # self.assertTrue(req.META.get('apianalytics-startedDateTime') > 100)
    # self.assertNotIn(self.whitespace, response.content)
