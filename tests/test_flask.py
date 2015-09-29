import time

from unittest import TestCase
from flask import Flask

from galileoanalytics import capture as Capture
from galileoanalytics.middleware import FlaskMiddleware
from tests.helpers import host, zmq_pull_once

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
    self.app.wsgi_app = FlaskMiddleware(self.app.wsgi_app, 'SERVICE-TOKEN', 'ENVIRONMENT', host())

    self.client = self.app.test_client()


  def tearDown(self):
    Capture.disconnect()

  @property
  def middleware(self):
    return self._middleware

  def test_get(self):
    recv = self.client.get('/get?foo=bar', headers={'CONTENT_TYPE': 'text/plain', 'X-Custom': 'custom'})

    self.assertIn('200 OK', recv.status)
    self.assertIn('Hello', str(recv.data))

    version, json = zmq_pull_once(host())

    self.assertTrue(json['har']['log']['entries'][0]['timings']['wait'] >= 10)

  def test_post(self):
    recv = self.client.post('/post', data='post data')

    self.assertIn('200 OK', recv.status)
    self.assertIn('Hello', str(recv.data))

    version, json = zmq_pull_once(host())

    self.assertTrue(json['har']['log']['entries'][0]['timings']['wait'] >= 10)
