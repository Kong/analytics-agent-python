DEFAULT_HOST = 'collector.galileo.mashape.com'

class BaseTransport(object):

  def __init__(self, host=DEFAULT_HOST):
    self.host = host
    self.connected = False

  def connect(self):
    '''
      Connect to the collector.
    '''
    pass

  def disconnect(self):
    '''
      Disconnect from the collector.
    '''
    pass

  def send(self, alf):
    '''
      Deliver ALF to the collector.
    '''
    pass
