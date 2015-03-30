from __future__ import unicode_literals

from datetime import datetime
from django.conf import settings

from apianalytics import capture as Capture
from apianalytics.alf import Alf


class DjangoMiddleware(object):

  def __init__(self):
    self.serviceToken = getattr(settings, 'APIANALYTICS_SERVICE_TOKEN', 'None')

    if self.serviceToken == None:
     raise AttributeError("'APIANALYTICS_SERVICE_TOKEN' setting is not found.")

  # def headers

  def process_request(self, request):
    request.startedDateTime = datetime.utcnow()

  def process_response(self, request, response):
    # import pdb
    # pdb.set_trace()

    # TODO Handle HttpResponse and StreamingHttpResponse
    startDateTime = request.startedDateTime
    alf = Alf(self.serviceToken)
    alf.addEntry({
      'startDateTime': request.startedDateTime.isoformat(),
      'request': {
        # WIP
      },
      'response': {
        # WIP
      },
      'timings': {
        # WIP
      }
    })

    Capture.record(alf.to_json())

    return response

