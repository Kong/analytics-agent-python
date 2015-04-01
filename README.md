Python Agent
============

The Python agent for [API Analytics](https://apianalytics.com)


Requirements
------------

This library requires `libzmq` and `libzmq-dev` to be installed.


Installation
------------

Install off PyPI.

```shell
pip install apianalytics
```

### Django

Add the following middleware:

```python
MIDDLEWARE_CLASSES = (
  'apianalytics.middleware.DjangoMiddleware',
)
```
