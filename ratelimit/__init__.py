from math import floor

import time
import sys
import threading

def rate_limited(period=1, every=1.0):
    '''
    Prevent a method from being called
    if it was previously called before
    a time widows has elapsed.

    :param int period: Maximum method invocations within a period. Must be greater than 0.
    :param float every: A dampening factor (in seconds). Can be any number greater than 0.
    :return: Decorated function that will forward method invocations if the time window has elapsed.
    :rtype: function
    '''
    frequency = abs(every) / float(clamp(period))
    def decorator(func):
        '''
        Extend the behaviour of the following
        function, forwarding method invocations
        if the time window hes elapsed.

        :param function func: The function to decorate.
        :return: Decorated function.
        :rtype: function
        '''

        # To get around issues with function local scope
        # and reassigning variables, we wrap the time
        # within a list. When updating the value we're
        # not reassigning `last_called`, which would not
        # work, but instead reassigning the value at a
        # particular index.
        last_called = [0.0]

        # Add thread safety
        lock = threading.RLock()

        def wrapper(*args, **kargs):
            '''Decorator wrapper function'''
            with lock:
                elapsed = time.time() - last_called[0]
                left_to_wait = frequency - elapsed
                if left_to_wait > 0:
                    time.sleep(left_to_wait)
                last_called[0] = time.time()
            return func(*args, **kargs)
        return wrapper
    return decorator

def clamp(value):
    '''
    Clamp integer between 1 and max

    There must be at least 1 method invocation
    made over the time period. Make sure the
    value passed is at least 1 and is not a
    fraction of an invocation.

    :param float value: The number of method invocations.
    :return: Clamped number of invocations.
    :rtype: int
    '''
    return max(1, min(sys.maxsize, floor(value)))

__all__ = [
    'rate_limited'
]
