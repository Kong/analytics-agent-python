Python Agent
============

The Python agent for [API Analytics](https://apianalytics.com)


Requirements
------------

This library uses [ZeroMQ](http://zeromq.org/intro:get-the-software). Make sure its installed.


Installation
------------

1. Install off PyPI.

    ```shell
    pip install apianalytics
    ```

2. Follow the install instructions for your specific framework, below.


### Django

Add the following middleware and setting in `settings.py`:

```python
MIDDLEWARE_CLASSES = (
  'apianalytics.middleware.DjangoMiddleware',
)

# API Analytics
APIANALYTICS_SERVICE_TOKEN = 'SERVICE_TOKEN'
```

### Flask

Add the middleware to `wsgi_app`:

```python
from apianalytics.middleware import WsgiMiddleware as ApiAnalytics
from flask import Flask

app = Flask(__name__)
app.wsgi_app = ApiAnalytics(app.wsgi_app, 'SERVICE_TOKEN') # Attach middleware

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
from apianalytics.middleware import WsgiMiddleware as ApiAnalytics
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

  app = ApiAnalytics(app, 'SERVICE_TOKEN') # 

  server = make_server('0.0.0.0', 8080, app)
  server.serve_forever()
```
