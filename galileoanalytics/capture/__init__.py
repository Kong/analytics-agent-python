try:
  # Attempt ZMQ
  import zmq

  from .zmq import record, connect, disconnect
except ImportError as e:
  # HTTP Fallback
  from .http import record, connect, disconnect
