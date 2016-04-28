from mashape_analytics.capture import Capture

class WsgiMiddleware(object):

  def __init__(self, app, serviceToken, environment=None, log_bodies='none', retry_count=0, connection_timeout=30, flush_timeout=2, queue_size=1000, host=None, port=None, fail_log_path=None):
    self.app = app
    self.serviceToken = serviceToken
    self.environment = environment
    self.log_bodies = log_bodies
    self.retry_count = retry_count
    self.connection_timeout = connection_timeout
    self.flush_timeout = flush_timeout
    self.queue_size = queue_size
    self.host = host
    self.port = port
    self.fail_log_path = fail_log_path

    self.connection_pool

    if host is not None:
      Capture.DEFAULT_HOST = host
