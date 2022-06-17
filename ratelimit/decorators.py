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

from ratelimit.exception import RateLimitException
from ratelimit.utils import now

class RateLimitDecorator(object):
    '''
    Rate limit decorator class.
    '''
    def __init__(
            self,
            calls=15,
            period=900,
            clock=now(),
            raise_on_limit=True,
            threshold=None,
            threshold_method=None
    ):
        '''
        Instantiate a RateLimitDecorator with some sensible defaults. By
        default the Twitter rate limiting window is respected (15 calls every
        15 minutes).

        :param int calls: Maximum function invocations allowed within a time period.
        :param float period: An upper bound time period (in seconds) before the rate limit resets.
        :param function clock: An optional function retuning the current time.
        :param bool raise_on_limit: A boolean allowing the caller to avoiding rasing an exception.
        :param float threshold: Optional fraction of the maximum number of available requests
         under which calls invoke method, e.g: 0.2 to trigger at 20% remaining requests.
        :param threshold_method: An optional method to invoke when hitting the threshold.
        '''
        self.clamped_calls = max(1, min(sys.maxsize, floor(calls)))
        self.period = period
        self.raise_on_limit = raise_on_limit
        self.threshold = threshold
        self.threshold_method = threshold_method
        self.clock = clock

        # Initialise the decorator state.
        self.last_update = clock()
        self.allowance = self.clamped_calls

        # Add thread safety.
        self.lock = threading.RLock()

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
            with self.lock:
                allowance_growth_per_second = self.clamped_calls / self.period

                seconds_elapsed = self.clock() - self.last_update
                self.allowance += floor(seconds_elapsed) * allowance_growth_per_second
                self.last_update = self.clock()

                if self.allowance > self.clamped_calls:
                    self.allowance = self.clamped_calls

                if self.threshold is not None and self.threshold_method is not None:
                    threshold_allowance = self.threshold * self.clamped_calls
                    if self.allowance < threshold_allowance:
                        self.threshold_method()
                if self.allowance < 1.0:
                    period_renaming = self.__period_remaining()
                    if self.raise_on_limit:
                        raise RateLimitException('too many calls', period_renaming)
                    return None
                self.allowance -= 1.0
            return func(*args, **kargs)

        return wrapper

    def __period_remaining(self):
        '''
        Return the period remaining for the current rate limit window.

        :return: The remaing period.
        :rtype: float
        '''
        return (1.0 - self.allowance) / (self.clamped_calls / self.period)

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
    return wrapper
