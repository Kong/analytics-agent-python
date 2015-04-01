from apianalytics import capture as Capture

# Setup a Django environment
from django.conf import settings
settings.configure(
  INSTALLED_APPS=['apianalytics'],
  ALLOWED_HOSTS=['testserver'],
  APIANALYTICS_SERVICE_TOKEN='SERVICE-TOKEN',
  APIANALYTICS_HOST='tcp://127.0.0.1:2200'
)

from .test_django import *
