from ratelimit import limits, RateLimitException
from tests import unittest, clock

class TestDecorator(unittest.TestCase):

    @limits(calls=1, period=10, clock=clock)
    def increment(self):
        '''
        Increment the counter at most once every 10 seconds.
        '''
        self.count += 1

    def setUp(self):
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
