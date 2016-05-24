# Mashape Analytics Python Agent

> for more information on Mashape Analytics, please visit [apianalytics.com](https://www.apianalytics.com)

## Installation

```sh
pip install mashape-analytics
```

If you're using Mac OS X. You may need [virtualenv](https://virtualenv.pypa.io/en/latest/). This is especially the case for El Capitan.

## Usage

### Django

Add the following middleware and setting in `settings.py`:

```python
MIDDLEWARE_CLASSES = (
  'mashapeanalytics.middleware.DjangoMiddleware',
)

# Mashape Analytics
MASHAPE_ANALYTICS_SERVICE_TOKEN = 'SERVICE_TOKEN' # Replace with your App Service Token
MASHAPE_ANALYTICS_ENVIRONMENT = 'production' # Leave blank for default, or replace with your Environment ID
```

**Note:** See [Django Configurations](https://github.com/Mashape/analytics-agent-python/wiki/Django-Configurations) for a full list of configuration properties.

### Flask

Add the middleware to `wsgi_app`:

```python
from mashapeanalytics.middleware import FlaskMiddleware as MashapeAnalytics
from flask import Flask

app = Flask(__name__)
app.wsgi_app = MashapeAnalytics(app.wsgi_app, 'SERVICE_TOKEN', 'production') # Attach middleware with environment, `production`

@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
```

**Note:** See [WSGI Configurations](https://github.com/Mashape/analytics-agent-python/wiki/WSGI-Configurations) for a full list of configuration properties.

### Pyramid

This example starts from [Pyramid's simplest application](http://docs.pylonsproject.org/docs/pyramid/en/latest/index.html).

Wrap the middleware to `app`:

```python
from mashapeanalytics.middleware import WsgiMiddleware as MashapeAnalytics
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response


def hello_world(request):
  return Response('Hello %(name)s!' % request.matchdict)

if __name__ == '__main__':
  config = Configurator()
  config.add_route('hello', '/hello/{name}')
  config.add_view(hello_world, route_name='hello')
  app = config.make_wsgi_app()

  app = MashapeAnalytics(app, 'SERVICE_TOKEN', 'production') # Attach middleware with environment, `production`

  server = make_server('0.0.0.0', 8080, app)
  server.serve_forever()
```

**Note:** See [WSGI Configurations](https://github.com/Mashape/analytics-agent-python/wiki/WSGI-Configurations) for a full list of configuration properties.

### Pylons

Add the middleware to your ini file.

```ini
[filter:mashape_analytics]
use = egg:mashape_analytics#mashape_analytics
serviceToken = SERVICE_TOKEN
environment = production

[pipeline]
pipeline = mashape_analytics my_application
```

**Note:** See [WSGI Configurations](https://github.com/Mashape/analytics-agent-python/wiki/WSGI-Configurations) for a full list of configuration properties.

## Copyright and license

Copyright Mashape Inc, 2015.

Licensed under [the MIT License](https://github.com/mashape/analytics-agent-python/blob/master/LICENSE)
