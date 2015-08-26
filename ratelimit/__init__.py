import time

def rate_limited(period, damping = 1.0):
  '''
  Prevent a method from being called
  if it was previously called before
  a time widows has elapsed.

  :param period: The time window after which method invocations can continue.
  :param damping: A factor by which to dampen the time window.
  :return function: Decorated function that will forward method invocations if the time window has elapsed.
  '''
  frequency = damping / float(period)
  def decorate(func):
    last_called = [0.0]
    def func_wrapper(*args, **kargs):
      elapsed = time.clock() - last_called[0]
      left_to_wait = frequency - elapsed
      if left_to_wait > 0:
        time.sleep(left_to_wait)
      ret = func(*args, **kargs)
      last_called[0] = time.clock()
      return ret
    return func_wrapper
  return decorate
