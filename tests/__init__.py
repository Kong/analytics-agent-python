from galileoanalytics import capture as Capture

# Setup a Django environment
from django.conf import settings
settings.configure(
  INSTALLED_APPS=['galileoanalytics'],
  ALLOWED_HOSTS=['testserver'],
  MASHAPE_ANALYTICS_SERVICE_TOKEN='SERVICE-TOKEN',
  MASHAPE_ANALYTICS_ENVIRONMENT='ENVIRONMENT',
  MASHAPE_ANALYTICS_HOST='tcp://127.0.0.1:56000'
)

from .test_django import *
from .test_flask import *
from .test_wsgi import *
from .test_pyramid import *
