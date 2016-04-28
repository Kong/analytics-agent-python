import ujson

from six.moves.urllib import urllib2

class HttpTransport(object):
  def __init__(self, host):
    self.host = host

  def send(self, alfs):
    payload = ujson.dumps(alfs)
    req = urllib2.Request(self.host, payload)
    response = urllib2.urlopen(req)
