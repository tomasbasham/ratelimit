'''
Function decorator for rate limiting

This module provides a functon decorator that can be used to wrap a function
such that it will raise an exception if the number of calls to that function
exceeds a maximum within a specified time window.

For examples and full documentation see the README at
https://github.com/tomasbasham/ratelimt
'''
from ratelimit.decorator import RateLimitDecorator
from ratelimit.exception import RateLimitException

limits = RateLimitDecorator

__all__ = [
    'RateLimitException',
    'limits'
]

__version__ = '2.0.0'
