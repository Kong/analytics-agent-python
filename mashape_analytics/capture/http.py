import multiprocessing
import os
import time
#
# the_queue = multiprocessing.Queue()
#
#
# def worker_main(queue):
#     print os.getpid(),"working"
#     while True:
#         item = queue.get(True)
#         print os.getpid(), "got", item
#         time.sleep(1) # simulate a "long" operation
#
# the_pool = multiprocessing.Pool(3, worker_main,(the_queue,))
# #                            don't forget the coma here  ^
#
# for i in range(5):
#     the_queue.put("hello")
#     the_queue.put("world")
#
#
# time.sleep(10)



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


# batch_thread = Thread(target=send, args=(work_queue,))
# batch_thread.start()
# batch_thread.join()
