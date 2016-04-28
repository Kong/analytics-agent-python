import ujson
import requests

class HttpTransport(object):
  def __init__(self, host, port=443, connection_timeout=30):
    if port == 443:
      self.url = 'https://%s/1.1.0/batch' % host
    elif port == 80:
      self.url = 'http://%s/1.1.0/batch' % host
    else:
      self.url = 'http://%s:%d/1.1.0/batch' % (host, port)
    self.connection_timeout = connection_timeout

  def send(self, alfs):
    payload = ujson.dumps(alfs)
    response = requests.post(self.url, data=payload, timeout=self.connection_timeout, headers={'Content-Type': 'application/json'})

    print reponse.text
