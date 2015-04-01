import zmq
from threading import Thread

from apianalytics import capture as Capture


def zmq_pull_once(host):
  socket = Capture.context.socket(zmq.PULL)
  socket.bind(host)

  msg = socket.recv_json()
  return msg

def host():
  return 'tcp://127.0.0.1:2200'
