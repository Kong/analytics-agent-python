import ujson
import requests

class HttpTransport(object):
  def __init__(self, host, port=443, connection_timeout=30, retry_count=0):
    if port == 443:
      self.url = 'https://%s/1.1.0/batch' % host
    elif port == 80:
      self.url = 'http://%s/1.1.0/batch' % host
    else:
      self.url = 'http://%s:%d/1.1.0/batch' % (host, port)
    self.connection_timeout = connection_timeout
    self.retry_count = retry_count

  def send(self, alfs):
    payload = ujson.dumps([dict(alf) for alf in alfs])

    with requests.Session() as s:
      s.mount('http://', requests.adapters.HTTPAdapter(max_retries=self.retry_count))
      s.mount('https://', requests.adapters.HTTPAdapter(max_retries=self.retry_count))

      response = s.post(self.url, data=payload, timeout=self.connection_timeout, headers={'Content-Type': 'application/json'})
      # print response.text
