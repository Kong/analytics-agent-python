import socket

from datetime import datetime

from apianalytics import capture as Capture
from apianalytics.alf import Alf

class WsgiMiddleware(object):
  def __init__(self, app, serviceToken):
    self.app = app
    self.serviceToken = serviceToken

  def countBytes(self, env, data):
    print 'buffering: %s' % data

    env['apianalytics.responseContentSize'] += len(data)

    return data

  def host(self, env):
    if env.get('HTTP_X_FORWARDED_HOST', False):
      return env['HTTP_X_FORWARDED_HOST'].split(',')[-1]
    elif (env['wsgi.url_scheme'] == 'http' and env['SERVER_PORT'] == '80') or (env['wsgi.url_scheme'] == 'https' and env['SERVER_PORT'] == '443'):
      return env['HTTP_HOST'] or env['HTTP_HOST']
    else:
      return env['HTTP_HOST'] or '%(SERVER_NAME)s:%(SERVER_PORT)s'.format(env)


  def absoluteUri(self, env):
    return '%s://%s'.format(env['wsgi.url_scheme'], self.host(env), env['PATH_INFO'])

  def __call__(self, env, start_response):

    # Wrap start_response function
    def wrapped_start_response(status, response_headers, exc_info=None):
      env['apianalytics.responseStatusCode'] = int(status[0:3])
      env['apianalytics.responseReasonPhrase'] = status[4:]
      env['apianalytics.responseHeaders'] = response_headers
      write = start_response(status, response_headers, exc_info)
      def wrapped_write(body): write(self.countBytes(env, body))
      return wrapped_write

    env['apianalytics.startedDateTime'] = datetime.utcnow()
    env['apianalytics.responseContentSize'] = 0

    # Capture response body from iterable
    iterable = None
    try:
      iterable = self.app(env, wrapped_start_response)
      for data in iterable:
        yield self.countBytes(env, data)
    finally:
      if hasattr(iterable, 'close'):
        iterable.close()

      # Construct and send ALF
      import pprint
      print 'WSGI Middleware Request'
      pprint.pprint(env)

      alf = Alf(self.serviceToken)
      alf.addEntry({
        'startedDateTime': env['apianalytics.startedDateTime'].isoformat() + 'Z', # HACK for apianalytics server to validate date
        'serverIpAddress': socket.gethostbyname(socket.gethostname()),
        'request': {
          'method': env['REQUEST_METHOD'],
          'url': self.absoluteUri(env),
          'httpVersion': env['SERVER_PROTOCOL'],
          # 'queryString': requestQueryString,
          # 'headers': requestHeaders,
          # 'headersSize': requestHeaderSize,
          'content': {
            # 'size': requestContentSize,
            # 'mimeType': request.META.get('CONTENT_TYPE', 'application/octet-stream')
          },
          # 'bodySize': requestHeaderSize + requestContentSize
        },
        # 'response': {
        #   'status': response.status_code,
        #   'statusText': response.reason_phrase,
        #   'httpVersion': 'HTTP/1.1',
        #   'headers': responseHeaders,
        #   'headersSize': responseHeadersSize,
        #   'content': {
        #     'size': responseContentSize,
        #     'mimeType': response._headers.get('content-type', (None, 'application/octet-stream'))[-1]
        #   },
        #   'bodySize': responseHeadersSize + responseContentSize
        # },
        # 'timings': {
        #   'send': 0,
        #   'wait': int(round((datetime.utcnow() - request.startedDateTime).total_seconds() * 1000)),
        #   'receive': 0
        # }
      })
