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

Add the FlaskMiddleware to `wsgi_app`:

```python
from apianalytics.middleware import FlaskMiddleware
from flask import Flask

app = Flask(__name__)
app.wsgi_app = FlaskMiddleware(app, 'SERVICE_TOKEN') # Attach middleware

@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
```
