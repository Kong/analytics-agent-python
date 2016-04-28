import json
import six

@six.python_2_unicode_compatible
class Alf(object):
  '''
  API Logging Format (ALF) Object v1.1.0
  '''

  def __init__(self, serviceToken, environment, entries=[]):
    self.serviceToken = serviceToken
    self.environment = environment
    self.entries = entries

  def __str__(self):
    return json.dumps(dict(self), indent=2)

  def __iter__(self):
    yield ('version', '1.1.0')
    yield ('serviceToken', self.serviceToken)
    yield ('environment', self.environment)
    yield ('har', {
      'log': {
        'creator': {
          'name': 'mashape-analytics-agent-python',
          'version': '3.0.0'
        },
        'entries': self.entries
      }
    })

  def addEntry(self, entry):
    self.entries.append(entry)
