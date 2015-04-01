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

Add the following middleware and setting:

```python
MIDDLEWARE_CLASSES = (
  'apianalytics.middleware.DjangoMiddleware',
)

# API Analytics
APIANALYTICS_SERVICE_TOKEN = 'SERVICE_TOKEN'
```
