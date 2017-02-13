from math import floor

import time
import sys

def rate_limited(period = 1, every = 1.0):
  '''
  Prevent a method from being called
  if it was previously called before
  a time widows has elapsed.

  :param period: The number of method invocation allowed over a time period. Must be greater than or equal to 1.
  :param every: A factor by which to dampen the time window (in seconds). Can be any number greater than 0.
  :return function: Decorated function that will forward method invocations if the time window has elapsed.
  '''
  frequency = abs(every) / float(clamp(period))
  def decorator(func):

    # To get around issues with function local scope
    # and reassigning variables, we wrap the time
    # within a list. When updating the value we're
    # not reassigning `last_called`, which would not
    # work, but instead reassigning the value at a
    # particular index.
    last_called = [0.0]

    def wrapper(*args, **kargs):
      elapsed = time.clock() - last_called[0]
      left_to_wait = frequency - elapsed
      if left_to_wait > 0:
        time.sleep(left_to_wait)
      ret = func(*args, **kargs)
      last_called[0] = time.clock()
      return ret
    return wrapper
  return decorator

def clamp(value):
  '''
  There must be at least 1 method invocation
  made over the time period. Make sure the
  value passed is at least one and it not
  a fraction of an invocation (wtf, like???)

  :param value: The number of method invocations.
  :return int: Clamped number of invocations.
  '''
  return max(1, min(sys.maxsize, floor(value)))

__all__ = [
  'rate_limited'
]
