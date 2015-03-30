import zmq
from threading import Thread

from apianalytics import capture as Capture


def zmq_pull_once(host=Capture.DEFAULT_HOST):
  socket = Capture.context.socket(zmq.PULL)
  socket.bind(host)

  msg = socket.recv_json()
  return msg
