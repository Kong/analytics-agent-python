import os
import re
import socket

from six.moves import cStringIO
from datetime import datetime
from six.moves.urllib.parse import parse_qs
from six.moves.http_cookies import SimpleCookie

from werkzeug.wrappers import Request

from mashapeanalytics.transport import HttpTransport
from mashapeanalytics.alf import Alf

class WsgiMiddleware(object):
  def __init__(self, app, serviceToken, environment=None, host='collector.galileo.mashape.com', port=443, connection_timeout=30, retry_count=0):
    self.app = app
    self.serviceToken = serviceToken
    self.environment = environment

    self.transport = HttpTransport(host, int(port), int(connection_timeout), int(retry_count))

  def count_response_content_size(self, env, data):
    env['MashapeAnalytics.responseContentSize'] += len(data)

    return data

  def host(self, env):
    if env.get('HTTP_X_FORWARDED_HOST', False):
      return env['HTTP_X_FORWARDED_HOST'].split(',')[-1]
    elif (env['wsgi.url_scheme'] == 'http' and env['SERVER_PORT'] == '80') or (env['wsgi.url_scheme'] == 'https' and env['SERVER_PORT'] == '443'):
      return env['HTTP_HOST'] or env['HTTP_HOST']
    else:
      return env['HTTP_HOST'] or '{SERVER_NAME}:{SERVER_PORT}'.format(env)

  def absolute_uri(self, env):
    queryString = ('?' if env.get('QUERY_STRING', False) else '')
    queryString += env.get('QUERY_STRING', '')

    return '{0}://{1}{2}{3}'.format(env['wsgi.url_scheme'], self.host(env), env['PATH_INFO'], queryString)

  def request_header_size(self, env):
    # {METHOD} {URL} {HTTP_PROTO}\r\n = 4 extra characters for space between method and url, and `\r\n`
    queryString = (1 if env.get('QUERY_STRING', False) else 0)  # `?` to start query string if exists
    queryString += len(env.get('QUERY_STRING', '')) # Rest of query string

    first_line = len(env['REQUEST_METHOD']) + len(env['PATH_INFO']) + queryString + len(env['SERVER_PROTOCOL']) + 4

    # {KEY}: {VALUE}\n\r = 4 extra characters for `: ` and `\n\r` minus `HTTP_` in the KEY is -1
    header_fields = sum([(len(header) + len(value) - 1) for (header, value) in env.items() if header.startswith('HTTP_')])

    last_line = 2 # /r/n

    return first_line + header_fields + last_line

  def request_header_name(self, header):
    return re.sub('_', '-', re.sub('^HTTP_', '', header))

  def response_header_size(self, env):
    # HTTP/1.1 {STATUS} {STATUS_TEXT} = 11 extra spaces
    first_line = len(str(env['MashapeAnalytics.responseStatusCode'])) + len(env['MashapeAnalytics.responseReasonPhrase']) + 11

    # {KEY}: {VALUE}\n\r = 4 extra characters `: ` and `\n\r`
    header_fields = sum([(len(header) + len(value) + 4) for (header, value) in env['MashapeAnalytics.responseHeaders']])

    return first_line + header_fields

  def client_address(self, env):
    ip = env.get('HTTP_X_FORWARDED_FOR', env.get('REMOTE_ADDR', None))

    if ip:
      return ip.split(',')[0]

  def wrap_start_response(self, env, start_response):
    def wrapped_start_response(status, response_headers, exc_info=None):
      env['MashapeAnalytics.responseStatusCode'] = int(status[0:3])
      env['MashapeAnalytics.responseReasonPhrase'] = status[4:]
      env['MashapeAnalytics.responseHeaders'] = response_headers
      write = start_response(status, response_headers, exc_info)
      def wrapped_write(body): write(self.count_response_content_size(env, body))
      return wrapped_write

    return wrapped_start_response

  def __call__(self, env, start_response):
    env['MashapeAnalytics.startedDateTime'] = datetime.utcnow()
    env['MashapeAnalytics.responseContentSize'] = 0

    # Capture response body from iterable
    iterable = None
    try:
      for data in self.app(env, self.wrap_start_response(env, start_response)):
        yield self.count_response_content_size(env, data)
    finally:
      if hasattr(iterable, 'close'):
        iterable.close()

      # Construct and send ALF
      r = Request(env)

      requestHeaders = [{'name': self.request_header_name(header), 'value': value} for (header, value) in env.items() if header.startswith('HTTP_')]
      requestHeaderSize = self.request_header_size(env)
      requestQueryString = [{'name': name, 'value': value[0]} for name, value in parse_qs(env.get('QUERY_STRING', '')).items()]

      requestContentSize = r.content_length or 0

      responseHeaders = [{'name': header, 'value': value} for (header, value) in env['MashapeAnalytics.responseHeaders']]
      responseHeadersSize = self.response_header_size(env)

      responseContentTypeHeaders = [header for header in env['MashapeAnalytics.responseHeaders'] if header[0] == 'Content-Type']
      if len(responseContentTypeHeaders) > 0:
        responseMimeType = responseContentTypeHeaders[0][1]
      else:
        responseMimeType = 'application/octet-stream'

      alf = Alf(self.serviceToken, self.environment, self.client_address(env))
      entry = {
        'startedDateTime': env['MashapeAnalytics.startedDateTime'].isoformat() + 'Z', # HACK for MashapeAnalytics server to validate date
        'serverIPAddress': socket.gethostbyname(socket.gethostname()),
        'time': int(round((datetime.utcnow() - env['MashapeAnalytics.startedDateTime']).total_seconds() * 1000)),
        'request': {
          'method': env['REQUEST_METHOD'],
          'url': self.absolute_uri(env),
          'httpVersion': env['SERVER_PROTOCOL'],
          'cookies': [],
          'queryString': requestQueryString,
          'headers': requestHeaders,
          'headersSize': requestHeaderSize,
          'bodySize': requestContentSize
        },
        'response': {
          'status': env['MashapeAnalytics.responseStatusCode'],
          'statusText': env['MashapeAnalytics.responseReasonPhrase'],
          'httpVersion': 'HTTP/1.1',
          'cookies': [],
          'headers': responseHeaders,
          'headersSize': responseHeadersSize,
          'content': {
            'size': env['MashapeAnalytics.responseContentSize'],
            'mimeType': responseMimeType
          },
          'bodySize': env['MashapeAnalytics.responseContentSize'],
          'redirectURL': next((value for (header, value) in env['MashapeAnalytics.responseHeaders'] if header == 'Location'), '')
        },
        'cache': {},
        'timings': {
          'blocked': -1,
          'dns': -1,
          'connect': -1,
          'send': 0,
          'wait': int(round((datetime.utcnow() - env['MashapeAnalytics.startedDateTime']).total_seconds() * 1000)),
          'receive': 0,
          'ssl': -1
        }
      }
      if 'CONTENT_LENGTH' in env and env['CONTENT_LENGTH'] != '0':
        entry['request']['content'] = {
          'size': requestContentSize,
          'mimeType': env['CONTENT_TYPE'] or 'application/octet-stream'
        }
      alf.addEntry(entry)

      self.transport.send(alf.json)
