# Make it easier to access middleware with apianalytics.middlware.xxx
# i.e. from apianalytics.middleware import DjangoMiddleware


'''
Django Framework
'''
try:
  from django.conf import settings

  from apianalytics.middleware.django_middleware import DjangoMiddleware

except ImportError, e:
  pass


'''
Flask Framework
'''
try:
  import flask

  from apianalytics.middleware.wsgi_middleware import WsgiMiddleware as FlaskMiddleware
except ImportError, e:
  pass

'''
Pyramid Framework
'''
# TODO pyramid

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


