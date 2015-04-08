import zmq

DEFAULT_HOST='tcp://socket.apianalytics.com:5000'

connected = False
context = zmq.Context()
socket = None


def connect(host=None):
  global DEFAULT_HOST, connected, context, socket

  if connected:
    return

  if host is None:
    host = DEFAULT_HOST

  # print 'Connecting to %s' % host
  socket = context.socket(zmq.PUSH)
  socket.connect(host)
  connected = True


def record(alf):
  global connected, socket

  if not connected:
    connect()

  socket.send_json(alf)


def disconnect(host=None):
  global connected, socket

  if host is None:
    host = DEFAULT_HOST

  socket.disconnect(host)
  connected = False
