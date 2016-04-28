import ujson

from unittest import TestCase
from mashape_analytics.transport import HttpTransport

transport = HttpTransport('localhost', 12345, 30)

class TransportTest(TestCase):
  def setUp(self):
    pass

  def tearDown(self):
    pass

  def test_should_send_alf(self):
    pass
