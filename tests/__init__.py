from mashapeanalytics import capture as Capture

# Setup a Django environment
from django.conf import settings
settings.configure(
  INSTALLED_APPS=['apianalytics'],
  ALLOWED_HOSTS=['testserver'],
  ANALYTICS_SERVICE_TOKEN='SERVICE-TOKEN',
  ANALYTICS_ENVIRONMENT='ENVIRONMENT',
  ANALYTICS_HOST='tcp://127.0.0.1:2200'
)

from .test_django import *
from .test_flask import *
from .test_wsgi import *
from .test_pyramid import *
