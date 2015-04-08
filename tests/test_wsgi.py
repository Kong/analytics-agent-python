import time

from unittest import TestCase

from multiprocessing import Process
from urllib2 import urlopen
from werkzeug.test import Client
from wsgiref.simple_server import make_server

from apianalytics import capture as Capture
from apianalytics.middleware import WsgiMiddleware
from tests.helpers import host, zmq_pull_once

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
    self.app = WsgiMiddleware(create_app(), 'SERVICE-TOKEN', host())

  def tearDown(self):
    Capture.disconnect()

  @property
  def middleware(self):
    return self._middleware

  def test_get(self):
    client = Client(self.app)
    data, status, headers = client.open()
    data = ''.join(data)

    self.assertIn('Hello', data)

    alf = zmq_pull_once(host())

    self.assertEqual(alf['serviceToken'], 'SERVICE-TOKEN')
    self.assertEqual(alf['har']['log']['creator']['name'], 'apianalytics-python')
    self.assertEqual(alf['har']['log']['entries'][0]['request']['method'], 'GET')
    self.assertEqual(alf['har']['log']['entries'][0]['request']['url'], 'http://localhost/')
    self.assertEqual(alf['har']['log']['entries'][0]['response']['status'], 200)
    self.assertEqual(alf['har']['log']['entries'][0]['response']['statusText'], 'OK CUSTOM')
    self.assertEqual(alf['har']['log']['entries'][0]['response']['content']['mimeType'], 'text/plain')
    self.assertEqual(alf['har']['log']['entries'][0]['response']['content']['size'], 11)
    self.assertTrue(alf['har']['log']['entries'][0]['timings']['wait'] >= 10)
