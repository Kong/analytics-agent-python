import ujson
import requests

from threading import Timer, Thread, Event

class SendThread(Thread):
  '''Send ALF thread'''
  def __init__(self, url, alf, connection_timeout=30, retry_count=0):
    Thread.__init__(self)
    self._stop = Event()
    # self.threadID = threadID
    self.name = 'alf-send'
    self.url = url
    self.alf = alf
    self.connection_timeout = connection_timeout
    self.retry_count = retry_count

  def stop(self):
    self._stop.set()

  @property
  def stopped(self):
    return self._stop.isSet()

  def run(self):
    print 'sending to', self.url
    payload = ujson.dumps(dict(self.alf))

    with requests.Session() as s:
      s.mount('http://', requests.adapters.HTTPAdapter(max_retries=self.retry_count))
      s.mount('https://', requests.adapters.HTTPAdapter(max_retries=self.retry_count))

      response = s.post(self.url, data=payload, timeout=self.connection_timeout, headers={'Content-Type': 'application/json'})
      # log response.text

class HttpTransport(object):
  def __init__(self, host, port=443, connection_timeout=30, retry_count=0):
    if port == 443:
      self.url = 'https://%s/1.0.0/single' % host
    elif port == 80:
      self.url = 'http://%s/1.0.0/single' % host
    else:
      self.url = 'http://%s:%d/1.0.0/single' % (host, port)
    self.connection_timeout = connection_timeout
    self.retry_count = retry_count

  def send(self, alf):
    send_alf = SendThread(self.url, alf, self.connection_timeout, self.retry_count)
    send_alf.start()
    # Non-blocking
