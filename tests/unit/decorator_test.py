from unittest.mock import MagicMock
from ratelimit import limits, RateLimitException
from tests import unittest, clock


class TestDecorator(unittest.TestCase):
    threshold_method = MagicMock()

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
        threshold=0.5,
        threshold_method=threshold_method
    )
    def increment_threshold_no_exception(self):
        '''
        Increment the counter at most once every 10 seconds, invoking the threshold method when
        the threshold is reached, without raising an exception when reaching the rate limit.
        '''
        self.count += 1

    @limits(
        calls=4,
        period=10,
        clock=clock,
        raise_on_limit=True,
        threshold=0.5,
        threshold_method=threshold_method
    )
    def increment_threshold(self):
        '''
        Increment the counter at most once every 10 seconds, triggering the threshold method when
        the threshold is reached, while raising an exception when reaching the rate limit.
        '''
        self.count += 1

    def setUp(self):
        self.threshold_method.reset_mock()
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

    def test_threshold_no_exception(self):
        self.increment_threshold_no_exception()
        self.increment_threshold_no_exception()
        self.threshold_method.assert_called_once()

    def test_threshold(self):
        # These first 3 calls should not trigger the threshold method nor hit the rate limit
        self.increment_threshold()
        self.threshold_method.assert_not_called()

        self.increment_threshold()
        self.threshold_method.assert_not_called()

        self.increment_threshold()
        self.threshold_method.assert_not_called()

        # This call causes the allowance to drop under the threshold, triggering the threshold_method
        self.increment_threshold()
        self.threshold_method.assert_called_once()

        # This call is made while the allowance is still under the threshold value, triggering the
        # threshold_method once more while also blocking the request as the rate limit has been hit
        self.threshold_method.reset_mock()
        self.assertRaises(RateLimitException, self.increment_threshold)
        self.threshold_method.assert_called_once()
