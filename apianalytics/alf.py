import json
import six

@six.python_2_unicode_compatible
class Alf(object):
  '''
  API Logging Format (ALF) Object
  '''


  def __init__(self, serviceToken):
    self.serviceToken = serviceToken
    self.entries = []

  def __str__(self):
    return json.dumps(self.to_json())

  def to_json(self):
    return {
      'serviceToken': self.serviceToken,

      'har': {
        'log': {
          'version': '1.2',
          'creator': {
            'name': 'apianalytics-python',
            'version': '1.0.0'
          },
          'entries': self.entries
        }
      }
    }

  def addEntry(self, entry):
    self.entries.append(entry)

