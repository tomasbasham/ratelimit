'''
Rate limit utilty functions.
'''
import time

def now():
    '''
    Use monotonic time if available, otherwise fall back to the system clock.

    :return: Time function.
    :rtype: function
    '''
    if hasattr(time, 'monotonic'):
        return time.monotonic
    return time.time
