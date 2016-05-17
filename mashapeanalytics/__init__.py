import mashapeanalytics.middleware
import mashapeanalytics.alf
import mashapeanalytics.transport

def make_wsgi_app(app, global_config, **local_config):
  return mashapeanalytics.middleware.WsgiMiddleware(app, **local_config)
