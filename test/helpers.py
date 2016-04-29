from multiprocessing import Process, Queue
from wsgiref.simple_server import make_server, WSGIRequestHandler
from werkzeug.wrappers import Request

class QuietHandler(WSGIRequestHandler):
  def log_request(*args, **kw): pass

class app(object):
  def __init__(self, port, status, headers, response):
    def handler(environ, start_response):
      request = Request(environ)
      content_length = request.content_length
      self.queue.put({'url': request.url, 'body': environ['wsgi.input'].read(content_length)})
      start_response(status, headers)
      return [response]

    self.queue = Queue()
    options = {'handler_class': QuietHandler}
    self.server = make_server('127.0.0.1', port, handler, **options)

  def __enter__(self):
    def run_app(server):
      server.handle_request()

    # self.process = Process(target=run_app, args=(self.port, self.queue, self.status, self.headers, self.response))
    self.process = Process(target=run_app, args=(self.server,))
    self.process.start()

    return self.queue

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.process.join()
