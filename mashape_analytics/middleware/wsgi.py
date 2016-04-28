import socket
import base64

from werkzeug.wrappers import Request
from mashape_analytics.analytics import Analytics
from six import StringIO

MAX_CONTENT_SIZE = 30 * 1024 * 1024

class WsgiMiddleware(object):
  def __init__(self, app, serviceToken, environment=None, log_bodies='none', retry_count=0, connection_timeout=30, flush_timeout=2, queue_size=1000, host='collector.galileo.mashape.com', port=443, fail_log_path=None):
    self.app = app
    self.analytics = Analytics(host, port, batch_size, flush_timeout, connection_timeout)
    self.serviceToken = serviceToken
    self.environment = environment
    self.log_bodies = log_bodies
    self.retry_count = retry_count
    self.host = host
    self.port = port
    self.fail_log_path = fail_log_path
    self.serverIPAddress = ocket.gethostbyname(socket.gethostname())

  def request_body(self, environ):
      content_length = environ.get('CONTENT_LENGTH')
      if content_length:
          if content_length == '-1':
              # This is a special case, where the content length is basically undetermined
              body = environ['wsgi.input'].read(-1)
              content_length = len(body)
          else:
              content_length = int(content_length)
              body = environ['wsgi.input'].read(content_length)
          environ['wsgi.input'] = StringIO(body) # reset request body for the nested app
      else:
          content_length = 0
      return content_length, body

  def request_header_size(self, env):
    # {METHOD} {URL} {HTTP_PROTO}\r\n = 4 extra characters for space between method and url, and `\r\n`
    queryString = (1 if env.get('QUERY_STRING', False) else 0)  # `?` to start query string if exists
    queryString += len(env.get('QUERY_STRING', '')) # Rest of query string

    first_line = len(env['REQUEST_METHOD']) + len(env['PATH_INFO']) + queryString + len(env['SERVER_PROTOCOL']) + 4

    # {KEY}: {VALUE}\n\r = 4 extra characters for `: ` and `\n\r` minus `HTTP_` in the KEY is -1
    header_fields = sum([(len(header) + len(value) - 1) for (header, value) in env.items() if header.startswith('HTTP_')])

    last_line = 2 # /r/n

    return first_line + header_fields + last_line

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

  def __call__(self, env, start_response):
    env['MashapeAnalytics.startedDateTime'] = datetime.utcnow()

    # Track request details
    request = Request(environ)
    requestContentSize = request.content_length
    requestBodyCaptured = True
    if requestContentSize is None:
      # Could not access request body
      requestContentSize = 0
      requestBodyCaptured = False

    if requestBodyCaptured and requestContentSize <= MAX_CONTENT_SIZE:
      requestBody = environ['wsgi.input'].read(requestContentSize)
      env['wsgi.input'] = StringIO(requestBody) # reset request body for the nested app

      requestEncodedBody = base64.b64encode(requestBody)

    response_body = []
    def buffer_response(status, headers, exc_info=None):
      env['MashapeAnalytics.responseStatusCode'] = int(status[0:3])
      env['MashapeAnalytics.responseReasonPhrase'] = status[4:]
      env['MashapeAnalytics.responseHeaders'] = headers
      start_response(status, headers, exc_info)
      return response_body.append

    # track response details
    app_iter = self.app(env, buffer_response)
    response_body.extend(app_iter)
    if hasattr(app_iter, 'close'):
      appiter.close()
    response = b''.join(response_body)

    if len(response) <= MAX_CONTENT_SIZE:
      responseEncodedBody = base64.b64encode(response)

    entry = {
      'startedDateTime': env['MashapeAnalytics.startedDateTime'].isoformat() + 'Z', # FORCE UTC
      'serverIPAddress': self.serverIPAddress,
      'clientIPAddress': self.client_address(env),
      'time': int(round((datetime.utcnow() - env['MashapeAnalytics.startedDateTime']).total_seconds() * 1000)),
      'request': {
        'method': env['REQUEST_METHOD'],
        'url': request.url,
        'httpVersion': env['SERVER_PROTOCOL'],
        'queryString': [{'name': name, 'value': value[0]} for name, value in parse_qs(env.get('QUERY_STRING', '')).items()],
        'headers': [{'name': header[0], 'value': header[1]} for header in request.headers],
        'headersSize': self.request_header_size(env),
        'bodyCaptured': requestBodyCaptured,
        'bodySize': requestContentSize
      },
      'response': {
        'status': env['MashapeAnalytics.responseStatusCode'],
        'statusText': env['MashapeAnalytics.responseReasonPhrase'],
        'httpVersion': 'HTTP/1.1',
        'headers': [{'name': header, 'value': value} for (header, value) in env['MashapeAnalytics.responseHeaders']],
        'headersSize': self.response_header_size(env),
        'bodyCaptured': True,
        'bodySize': len(response),
        'redirectURL': next((value for (header, value) in env['MashapeAnalytics.responseHeaders'] if header == 'Location'), '')
      },
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

    if requestEncodedBody:
      entry['request']['postData'] = {
        'mimeType': request.headers['Content-Type'] or 'application/octet-stream',
        'encoding': 'base64',
        'text': requestEncodedBody
      }

    if responseEncodedBody:
      entry['response']['content'] = {
        'mimeType': [header for header in env['MashapeAnalytics.responseHeaders'] if header[0] == 'Content-Type'][0][1] or 'application/octet-stream',
        'encoding': 'base64',
        'text': responseEncodedBody
      }

    alf = Alf(self.serviceToken, self.environment, [entry])

    # import json
    # print json.dumps(alf.json, indent=2)

    self.analytics.submit(alf)

    return [response]
