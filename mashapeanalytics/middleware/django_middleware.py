from __future__ import unicode_literals

import re
import socket

from datetime import datetime
from django.conf import settings
from six.moves import cStringIO
from six.moves.urllib.parse import parse_qs

# from mashapeanalytics import capture as Capture
from mashapeanalytics.transport import HttpTransport
from mashapeanalytics.alf import Alf

from werkzeug.wrappers import Request

class DjangoMiddleware(object):

  def __init__(self):
    self.serviceToken = getattr(settings, 'MASHAPE_ANALYTICS_SERVICE_TOKEN', None)
    self.environment = getattr(settings, 'MASHAPE_ANALYTICS_ENVIRONMENT', None)

    host = getattr(settings, 'MASHAPE_ANALYTICS_HOST', 'collector.galileo.mashape.com')
    port = int(getattr(settings, 'MASHAPE_ANALYTICS_PORT', 443))
    connection_timeout = int(getattr(settings, 'MASHAPE_ANALYTICS_CONNECTION_TIMEOUT', 30))
    retry_count = int(getattr(settings, 'MASHAPE_ANALYTICS_RETRY_COUNT', 0))
    self.transport = HttpTransport(host, port, connection_timeout, retry_count)

    if self.serviceToken is None:
      raise AttributeError("'MASHAPE_ANALYTICS_SERVICE_TOKEN' setting is not found.")

  def process_request(self, request):
    request.META['MASHAPE_ANALYTICS.STARTED_DATETIME'] = datetime.utcnow()
    request.META['galileo.request'] = Request(request.META)

  def request_header_size(self, request):
    # {METHOD} {URL} HTTP/1.1\r\n = 12 extra characters for space between method and url, and ` HTTP/1.1\r\n`
    first_line = len(request.META.get('REQUEST_METHOD')) + len(request.get_full_path()) + 12

    # {KEY}: {VALUE}\n\r = 4 extra characters for `: ` and `\n\r` minus `HTTP_` in the KEY is -1
    header_fields = sum([(len(header) + len(value) - 1) for (header, value) in request.META.items() if header.startswith('HTTP_')])

    last_line = 2 # /r/n

    return first_line + header_fields + last_line

  def client_address(self, request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', None))

    if ip:
      return ip.split(',')[0]

  def response_header_size(self, response):
    # HTTP/1.1 {STATUS} {STATUS_TEXT} = 10 extra characters
    first_line = len(str(response.status_code)) + len(response.reason_phrase) + 10

    # {KEY}: {VALUE}\n\r = 4 extra characters `: ` and `\n\r`
    header_fields = sum([(len(header) + len(value) + 4) for (header, value) in response._headers.items()])

    return first_line + header_fields

  def process_response(self, request, response):
    startedDateTime = request.META.get('MASHAPE_ANALYTICS.STARTED_DATETIME', datetime.utcnow())

    requestHeaders = [{'name': re.sub('^HTTP_', '', header), 'value': value} for (header, value) in request.META.items() if header.startswith('HTTP_')]
    requestHeaderSize = self.request_header_size(request)
    requestQueryString = [{'name': name, 'value': (value[0] if len(value) > 0 else None)} for name, value in parse_qs(request.META.get('QUERY_STRING', '')).items()]

    r = request.META.get('galileo.request')
    requestContentSize = r.content_length or 0

    responseHeaders = [{'name': header, 'value': value[-1]} for (header, value) in response._headers.items()]
    responseHeadersSize = self.response_header_size(response)
    responseContentSize = len(response.content)

    alf = Alf(self.serviceToken, self.environment, self.client_address(request))
    alf.addEntry({
      'startedDateTime': startedDateTime.isoformat() + 'Z',
      'serverIpAddress': socket.gethostbyname(socket.gethostname()),
      'time': int(round((datetime.utcnow() - startedDateTime).total_seconds() * 1000)),
      'request': {
        'method': request.method,
        'url': request.build_absolute_uri(),
        'httpVersion': 'HTTP/1.1',
        'cookies': [],
        'queryString': requestQueryString,
        'headers': requestHeaders,
        'headersSize': requestHeaderSize,
        'content': {
          'size': requestContentSize,
          'mimeType': request.META.get('CONTENT_TYPE', 'application/octet-stream')
        },
        'bodySize': requestContentSize
      },
      'response': {
        'status': response.status_code,
        'statusText': response.reason_phrase,
        'httpVersion': 'HTTP/1.1',
        'cookies': [],
        'headers': responseHeaders,
        'headersSize': responseHeadersSize,
        'content': {
          'size': responseContentSize,
          'mimeType': response._headers.get('content-type', (None, 'application/octet-stream'))[-1]
        },
        'bodySize': responseHeadersSize + responseContentSize,
        'redirectURL': response._headers.get('location', ('location', ''))[-1]
      },
      'cache': {},
      'timings': {
        'blocked': -1,
        'dns': -1,
        'connect': -1,
        'send': 0,
        'wait': int(round((datetime.utcnow() - startedDateTime).total_seconds() * 1000)),
        'receive': 0,
        'ssl': -1
      }
    })

    self.transport.send(alf.json)

    return response
