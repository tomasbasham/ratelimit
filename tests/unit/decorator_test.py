from ratelimit import *
from tests import *

class TestDecorator(unittest.TestCase):

  def test_decorator(self):
    limiter = rate_limited(1)
    decorated = limiter(lambda: 'None')
    self.assertEqual(decorated(), 'None')
