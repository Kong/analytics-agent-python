from __future__ import unicode_literals

import re
import socket

from datetime import datetime
from django.conf import settings
from urlparse import parse_qs

from apianalytics import capture as Capture
from apianalytics.alf import Alf


class DjangoMiddleware(object):

  def __init__(self):
    self.serviceToken = getattr(settings, 'APIANALYTICS_SERVICE_TOKEN', None)
    host = getattr(settings, 'APIANALYTICS_HOST', None)

    if self.serviceToken is None:
      raise AttributeError("'APIANALYTICS_SERVICE_TOKEN' setting is not found.")

    if host is not None:
      Capture.DEFAULT_HOST = host

  def process_request(self, request):
    request.startedDateTime = datetime.utcnow()

  def request_header_size(self, request):
    # {METHOD} {URL} HTTP/1.1\r\n = 12 extra characters for space between method and url, and ` HTTP/1.1\r\n`
    first_line = len(request.META.get('REQUEST_METHOD')) + len(request.get_full_path()) + 12

    # {KEY}: {VALUE}\n\r = 4 extra characters for `: ` and `\n\r` minus `HTTP_` in the KEY is -1
    header_fields = sum([(len(header) + len(value) - 1) for (header, value) in request.META.items() if header.startswith('HTTP_')])

    last_line = 2 # /r/n

    return first_line + header_fields + last_line

  def response_header_size(self, response):
    # HTTP/1.1 {STATUS} {STATUS_TEXT} = 10 extra characters
    first_line = len(str(response.status_code)) + len(response.reason_phrase) + 10

    # {KEY}: {VALUE}\n\r = 4 extra characters `: ` and `\n\r`
    header_fields = sum([(len(header) + len(value) + 4) for (header, value) in response._headers.items()])

    return first_line + header_fields

  def process_response(self, request, response):
    requestHeaders = [{'name': re.sub('^HTTP_', '', header), 'value': value} for (header, value) in request.META.items() if header.startswith('HTTP_')]
    requestHeaderSize = self.request_header_size(request)
    requestQueryString = [{'name': name, 'value': (value[0] if len(value) > 0 else None)} for name, value in parse_qs(request.META.get('QUERY_STRING', '')).items()]
    requestContentSize = len(request.body)

    responseHeaders = [{'name': header, 'value': value[-1]} for (header, value) in response._headers.items()]
    responseHeadersSize = self.response_header_size(response)
    responseContentSize = len(response.content)

    alf = Alf(self.serviceToken)
    alf.addEntry({
      'startedDateTime': request.startedDateTime.isoformat() + 'Z',
      'serverIpAddress': socket.gethostbyname(socket.gethostname()),
      'request': {
        'method': request.method,
        'url': request.build_absolute_uri(),
        'httpVersion': 'HTTP/1.1',
        'queryString': requestQueryString,
        'headers': requestHeaders,
        'headersSize': requestHeaderSize,
        'content': {
          'size': requestContentSize,
          'mimeType': request.META.get('CONTENT_TYPE', 'application/octet-stream')
        },
        'bodySize': requestHeaderSize + requestContentSize
      },
      'response': {
        'status': response.status_code,
        'statusText': response.reason_phrase,
        'httpVersion': 'HTTP/1.1',
        'headers': responseHeaders,
        'headersSize': responseHeadersSize,
        'content': {
          'size': responseContentSize,
          'mimeType': response._headers.get('content-type', (None, 'application/octet-stream'))[-1]
        },
        'bodySize': responseHeadersSize + responseContentSize
      },
      'timings': {
        'send': 0,
        'wait': int(round((datetime.utcnow() - request.startedDateTime).total_seconds() * 1000)),
        'receive': 0
      }
    })

    # import json
    # print json.dumps(alf.json, indent=2)

    Capture.record(alf.json)

    return response

