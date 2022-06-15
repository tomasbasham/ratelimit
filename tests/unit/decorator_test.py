from unittest.mock import MagicMock
from ratelimit import limits, RateLimitException
from tests import unittest, clock


class TestDecorator(unittest.TestCase):
    treshold_method = MagicMock()

    @limits(calls=1, period=10, clock=clock)
    def increment(self):
        '''
        Increment the counter at most once every 10 seconds.
        '''
        self.count += 1

    @limits(calls=1, period=10, clock=clock, raise_on_limit=False)
    def increment_no_exception(self):
        '''
        Increment the counter at most once every 10 seconds, without raising an exception when
        reaching the rate limit.
        '''
        self.count += 1

    @limits(
        calls=1,
        period=10,
        clock=clock,
        raise_on_limit=False,
        treshold=0.5,
        treshold_method=treshold_method
    )
    def increment_treshold_no_exception(self):
        '''
        Increment the counter at most once every 10 seconds, invoking the treshold method when
        the treshold is reached, without raising an exception when reaching the rate limit.
        '''
        self.count += 1

    @limits(
        calls=4,
        period=10,
        clock=clock,
        raise_on_limit=True,
        treshold=0.5,
        treshold_method=treshold_method
    )
    def increment_treshold(self):
        '''
        Increment the counter at most once every 10 seconds, triggering the treshold method when
        the treshold is reached, while raising an exception when reaching the rate limit.
        '''
        self.count += 1

    def setUp(self):
        self.treshold_method.reset_mock()
        self.count = 0
        clock.increment(10)

    def test_increment(self):
        self.increment()
        self.assertEqual(self.count, 1)

    def test_exception(self):
        self.increment()
        self.assertRaises(RateLimitException, self.increment)

    def test_reset(self):
        self.increment()
        clock.increment(10)

        self.increment()
        self.assertEqual(self.count, 2)

    def test_no_exception(self):
        self.increment_no_exception()
        self.increment_no_exception()

        self.assertEqual(self.count, 1)

    def test_treshold_no_exception(self):
        self.increment_treshold_no_exception()
        self.increment_treshold_no_exception()
        self.treshold_method.assert_called_once()

    def test_treshold(self):
        # These first 3 calls should not trigger the treshold method nor hit the rate limit
        self.increment_treshold()
        self.treshold_method.assert_not_called()

        self.increment_treshold()
        self.treshold_method.assert_not_called()

        self.increment_treshold()
        self.treshold_method.assert_not_called()

        # This call causes the allowance to drop under the treshold, triggering the treshold_method
        self.increment_treshold()
        self.treshold_method.assert_called_once()

        # This call is made while the allowance is still under the treshold value, triggering the
        # treshold_method once more while also blocking the request as the rate limit has been hit
        self.treshold_method.reset_mock()
        self.assertRaises(RateLimitException, self.increment_treshold)
        self.treshold_method.assert_called_once()
