import zmq
import ujson
from threading import Thread

from mashapeanalytics import capture as Capture


def zmq_pull_once(host):
  socket = Capture.context.socket(zmq.PULL)
  socket.bind(host)

  data = socket.recv_string()
  version, msg = data.split(' ', 1)
  return version, ujson.decode(msg)

def host():
  return 'tcp://127.0.0.1:56000'
