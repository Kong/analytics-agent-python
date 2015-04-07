import os
import re
import socket

from datetime import datetime
from urlparse import parse_qs

from apianalytics import capture as Capture
from apianalytics.alf import Alf

class WsgiMiddleware(object):
  def __init__(self, app, serviceToken):
    self.app = app
    self.serviceToken = serviceToken

  def count_response_content_size(self, env, data):
    env['apianalytics.responseContentSize'] += len(data)

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
    first_line = len(str(env['apianalytics.responseStatusCode'])) + len(env['apianalytics.responseReasonPhrase']) + 11

    # {KEY}: {VALUE}\n\r = 4 extra characters `: ` and `\n\r`
    header_fields = sum([(len(header) + len(value) + 4) for (header, value) in env['apianalytics.responseHeaders']])

    return first_line + header_fields

  def __call__(self, env, start_response):

    # Wrap start_response function
    def wrapped_start_response(status, response_headers, exc_info=None):
      env['apianalytics.responseStatusCode'] = int(status[0:3])
      env['apianalytics.responseReasonPhrase'] = status[4:]
      env['apianalytics.responseHeaders'] = response_headers
      write = start_response(status, response_headers, exc_info)
      def wrapped_write(body): write(self.count_response_content_size(env, body))
      return wrapped_write

    env['apianalytics.startedDateTime'] = datetime.utcnow()
    env['apianalytics.responseContentSize'] = 0

    # Capture response body from iterable
    iterable = None
    try:
      iterable = self.app(env, wrapped_start_response)
      for data in iterable:
        yield self.count_response_content_size(env, data)
    finally:
      if hasattr(iterable, 'close'):
        iterable.close()

      # import pprint
      # pprint.pprint(env)

      # Construct and send ALF
      requestHeaders = [{'name': self.request_header_name(header), 'value': value} for (header, value) in env.items() if header.startswith('HTTP_')]
      requestHeaderSize = self.request_header_size(env)
      requestQueryString = [{'name': name, 'value': value} for name, value in parse_qs(env.get('QUERY_STRING', '')).items()]

      env['wsgi.input'].seek(0, os.SEEK_END)
      requestContentSize = env['wsgi.input'].tell()

      responseHeaders = [{'name': header, 'value': value} for (header, value) in env['apianalytics.responseHeaders']]
      responseHeadersSize = self.response_header_size(env)

      alf = Alf(self.serviceToken)
      entry = {
        'startedDateTime': env['apianalytics.startedDateTime'].isoformat() + 'Z', # HACK for apianalytics server to validate date
        'serverIpAddress': socket.gethostbyname(socket.gethostname()),
        'request': {
          'method': env['REQUEST_METHOD'],
          'url': self.absolute_uri(env),
          'httpVersion': env['SERVER_PROTOCOL'],
          'queryString': requestQueryString,
          'headers': requestHeaders,
          'headersSize': requestHeaderSize,
          'bodySize': requestHeaderSize + requestContentSize
        },
        'response': {
          'status': env['apianalytics.responseStatusCode'],
          'statusText': env['apianalytics.responseReasonPhrase'],
          'httpVersion': 'HTTP/1.1',
          'headers': responseHeaders,
          'headersSize': responseHeadersSize,
          'content': {
            'size': env['apianalytics.responseContentSize'],
            'mimeType': [header for header in env['apianalytics.responseHeaders'] if header[0] == 'Content-Type'][0][1] or 'application/octet-stream'
          },
          'bodySize': responseHeadersSize + env['apianalytics.responseContentSize']
        },
        'timings': {
          'send': 0,
          'wait': int(round((datetime.utcnow() - env['apianalytics.startedDateTime']).total_seconds() * 1000)),
          'receive': 0
        }
      }
      if env['CONTENT_LENGTH'] != '0':
        entry['request']['content'] = {
          'size': requestContentSize,
          'mimeType': env['CONTENT_TYPE'] or 'application/octet-stream'
        }
      alf.addEntry(entry)

      # pprint.pprint(alf.to_json())

      # import pdb
      # pdb.set_trace()

