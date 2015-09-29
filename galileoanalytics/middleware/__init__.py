# Make it easier to access middleware with mashapeanalytics.middlware.xxx
# i.e. from mashapeanalytics.middleware import DjangoMiddleware
# This is purely for discovery.

from galileoanalytics.middleware.wsgi_middleware import WsgiMiddleware

'''
Django Framework
'''
try:
  from django.conf import settings

  from galileoanalytics.middleware.django_middleware import DjangoMiddleware
except ImportError as e:
  pass


'''
Flask Framework
'''
try:
  import flask

  from galileoanalytics.middleware.wsgi_middleware import WsgiMiddleware as FlaskMiddleware
except ImportError as e:
  pass

'''
Pyramid Framework
'''
try:
  import pyramid

  from galileoanalytics.middleware.wsgi_middleware import WsgiMiddleware as PyramidMiddleware
except ImportError as e:
  pass

'''
Twisted Framework
'''
# TODO twisted

'''
Bottle Framework
'''
# TODO bottle

'''
CherryPy Framework
'''
# TODO cherry

'''
Pylons Framework
'''
# TODO pylons

'''
webpy Framework
'''
# TODO webpy

'''
web2py Framework
'''
# TODO web2py
