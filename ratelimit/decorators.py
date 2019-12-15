'''
Rate limit public interface.

This module includes the decorator used to rate limit function invocations.
Additionally this module includes a naive retry strategy to be used in
conjunction with the rate limit decorator.
'''
from functools import wraps
from math import floor

import time
import sys
import threading
import inspect
import asyncio

from ratelimit.exception import RateLimitException
from ratelimit.utils import now


class RateLimitDecorator(object):
    '''
    Rate limit decorator class.
    '''
    def __init__(self, calls=15, period=900, clock=now(), raise_on_limit=True):
        '''
        Instantiate a RateLimitDecorator with some sensible defaults. By
        default the Twitter rate limiting window is respected (15 calls every
        15 minutes).

        :param int calls: Maximum function invocations allowed within a time period.
        :param float period: An upper bound time period (in seconds) before the rate limit resets.
        :param function clock: An optional function retuning the current time.
        :param bool raise_on_limit: A boolean allowing the caller to avoiding rasing an exception.
        '''
        self.clamped_calls = max(1, min(sys.maxsize, floor(calls)))
        self.period = period
        self.clock = clock
        self.raise_on_limit = raise_on_limit

        # Initialise the decorator state.
        self.last_reset = clock()
        self.num_calls = 0

        # Add thread safety.
        self.lock = threading.RLock()

    def _check_limit_exceeded(self):
        with self.lock:
            period_remaining = self.__period_remaining()

            # If the time window has elapsed then reset.
            if period_remaining <= 0:
                self.num_calls = 0
                self.last_reset = self.clock()

            # Increase the number of attempts to call the function.
            self.num_calls += 1

            # If the number of attempts to call the function exceeds the
            # maximum then raise an exception.
            if self.num_calls > self.clamped_calls:
                if self.raise_on_limit:
                    raise RateLimitException('too many calls', period_remaining)
                return True
            return False

    def __call__(self, func):
        '''
        Return a wrapped function that prevents further function invocations if
        previously called within a specified period of time.

        :param function func: The function to decorate.
        :return: Decorated function.
        :rtype: function
        '''
        @wraps(func)
        def wrapper(*args, **kargs):
            '''
            Extend the behaviour of the decorated function, forwarding function
            invocations previously called no sooner than a specified period of
            time. The decorator will raise an exception if the function cannot
            be called so the caller may implement a retry strategy such as an
            exponential backoff.

            :param args: non-keyword variable length argument list to the decorated function.
            :param kargs: keyworded variable length argument list to the decorated function.
            :raises: RateLimitException
            '''
            if self._check_limit_exceeded():
                return
            return func(*args, **kargs)

        @wraps(func)
        async def async_wrapper(*args, **kargs):
            '''
            Does the same thing as `wrapper` but in async manner
            '''
            if self._check_limit_exceeded():
                return
            return await func(*args, **kargs)

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper

    def __period_remaining(self):
        '''
        Return the period remaining for the current rate limit window.

        :return: The remaing period.
        :rtype: float
        '''
        elapsed = self.clock() - self.last_reset
        return self.period - elapsed


def sleep_and_retry(func):
    '''
    Return a wrapped function that rescues rate limit exceptions, sleeping the
    current thread until rate limit resets.

    :param function func: The function to decorate.
    :return: Decorated function.
    :rtype: function
    '''
    @wraps(func)
    def wrapper(*args, **kargs):
        '''
        Call the rate limited function. If the function raises a rate limit
        exception sleep for the remaing time period and retry the function.

        :param args: non-keyword variable length argument list to the decorated function.
        :param kargs: keyworded variable length argument list to the decorated function.
        '''
        while True:
            try:
                return func(*args, **kargs)
            except RateLimitException as exception:
                time.sleep(exception.period_remaining)

    @wraps(func)
    async def async_wrapper(*args, **kargs):
        '''
        Does the same thing as `wrapper` but in async manner
        '''
        while True:
            try:
                return await func(*args, **kargs)
            except RateLimitException as exception:
                await asyncio.sleep(exception.period_remaining)

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return wrapper
