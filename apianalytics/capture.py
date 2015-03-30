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

  socket = context.socket(zmq.PUSH)
  socket.connect(host)
  connected = True


def record(alf):
  global connected, socket

  if not connected:
    connect()

  socket.send_json(alf)


def disconnect():
  global connected, socket

  socket.disconnect()
  connected = False
