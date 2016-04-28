from mashape_analytics import capture as Capture

# Setup a Django environment
from django.conf import settings
settings.configure(
  INSTALLED_APPS=['mashape_analytics'],
  ALLOWED_HOSTS=['testserver'],
  MASHAPE_ANALYTICS_SERVICE_TOKEN='SERVICE-TOKEN',
  MASHAPE_ANALYTICS_ENVIRONMENT='ENVIRONMENT',
  MASHAPE_ANALYTICS_HOST='tcp://127.0.0.1:56000'
)

import test_django
import test_flask
import test_wsgi
import test_pyramid
