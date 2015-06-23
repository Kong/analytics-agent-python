import time

from unittest import TestCase
from pyramid.config import Configurator
from pyramid.response import Response
from werkzeug.test import Client

from mashapeanalytics import capture as Capture
from mashapeanalytics.middleware import WsgiMiddleware
from tests.helpers import host, zmq_pull_once

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
    self.app = WsgiMiddleware(create_app(), 'SERVICE_TOKEN', 'ENVIRONMENT', host())

  def tearDown(self):
    Capture.disconnect()

  def test_get(self):
    client = Client(self.app)
    data, status, headers = client.open()
    data = ''.join(data)


    self.assertIn('Hello', data)

    version, alf = zmq_pull_once(host())

    self.assertTrue(alf['har']['log']['entries'][0]['timings']['wait'] >= 10)

