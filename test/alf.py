import ujson

from unittest import TestCase
from mashape_analytics.alf import Alf

class AlfTest(TestCase):
  def setUp(self):
    pass

  def tearDown(self):
    pass

  def test_should_create_an_alf(self):
    alf = Alf('service-token', 'environment', [{'entry': 1}])

    self.assertEqual('service-token', alf.serviceToken)
    self.assertEqual('environment', alf.environment)

    self.assertEqual(ujson.dumps({'version': '1.1.0', 'serviceToken': 'service-token', 'environment': 'environment', 'har': {'log': {'creator': {'name': 'mashape-analytics-agent-python', 'version': '3.0.0'}, 'entries': [{'entry': 1}]}}}), ujson.dumps(dict(alf)))
