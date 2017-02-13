from ratelimit import rate_limited
from tests import *

class TestDecorator(unittest.TestCase):

  @rate_limited(1, 2)
  def increment(self):
    '''
    Increment the counter at most once
    every 2 seconds.
    '''
    self.count += 1

  def setUp(self):
    self.count = 0

  def test_decorator(self):
    self.assertEqual(self.count, 0)
    self.increment()
    self.assertEqual(self.count, 1)
