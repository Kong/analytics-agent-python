from threading import Thread
from Queue import Queue, Empty
import itertools

DEFAULT_HOST='tcp://socket.analytics.mashape.com/1.0.0/batch'

batch_queue = Queue()
current_batch = []
connected = False

def connect(host=DEFAULT_HOST):
  # TODO set request obj
  # TODO ping
  connected = True

def flush():
  batch_queue.put(current_batch)
  current_batch = []

def record(alf):
  if not connected:
    connect()

  current_batch.append(alf)
  # TODO check for full

def send(queue):
  while True:
    batch = queue.get()

    # TODO Send batch
    # TODO upon error, add back into queue


batch_thread = Thread(target=send, args=(work_queue,))
batch_thread.start()
batch_thread.join()
