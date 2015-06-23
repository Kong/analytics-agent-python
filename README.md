Mashape Analytics Python Agent
===============================

The Python agent for [Mashape Analytics](https://apianalytics.com)


Requirements
------------

This library uses [ZeroMQ](http://zeromq.org/intro:get-the-software). Make sure its installed.


Installation
------------

1. Install off PyPI.

    ```shell
    pip install mashape-analytics
    ```

2. Follow the install instructions for your specific framework, below.

NOTE: Replace the service token and environment with your specific values from [API Analytics](https://apianalytics.com)


### Django

Add the following middleware and setting in `settings.py`:

```python
MIDDLEWARE_CLASSES = (
  'mashapeanalytics.middleware.DjangoMiddleware',
)

# API Analytics
ANALYTICS_SERVICE_TOKEN = 'SERVICE_TOKEN' # Replace with your App Service Token
ANALYTICS_ENVIRONMENT = 'production' # Replace with your Environment ID
```

### Flask

Add the middleware to `wsgi_app`:

```python
from mashapeanalytics.middleware import WsgiMiddleware as MashapeAnalytics
from flask import Flask

app = Flask(__name__)
app.wsgi_app = MashapeAnalytics(app.wsgi_app, 'SERVICE_TOKEN', 'production') # Attach middleware with environment, `production`

@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
```

### Pyramid

This example starts from [Pyramid's simpliest application](http://docs.pylonsproject.org/docs/pyramid/en/latest/index.html).

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
