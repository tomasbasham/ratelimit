import time
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

  def test_timing(self):
    for i in range(10):
      before = time.time()
      self.increment()
      after = time.time()
      # allow a 0.1 second error
      self.assertTrue((after-before - 2.0) < 0.1, "Function was executed too fast")
