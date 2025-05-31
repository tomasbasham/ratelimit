'''

'''

import aiounittest
import pytest
import inspect

from ratelimit import limits, RateLimitException, sleep_and_retry
from tests import clock
from unittest.mock import patch


async def async_func_to_test():
    '''
    Basic async function returning True
    '''
    return True


def sync_func_to_test():
    '''
    Basic sync function returning True
    '''
    return True


class TestDecorator(aiounittest.AsyncTestCase):
    '''
    Tests for asyncio integration with ratelimit
    '''

    @pytest.mark.asyncio
    async def test_takes_sync_and_async_func(self):
        '''
        Checks if sync/async wrapper selection works
        '''
        limited_sync = limits(calls=1, period=10, clock=clock)(sync_func_to_test)
        self.assertFalse(inspect.iscoroutinefunction(limited_sync))
        self.assertTrue(limited_sync())

        limited_async = limits(calls=1, period=10, clock=clock)(async_func_to_test)
        self.assertTrue(inspect.iscoroutinefunction(limited_async))
        self.assertTrue(await limited_async())

    @pytest.mark.asyncio
    async def test_async_function_raises(self):
        '''
        Checks if async limiting raises RateLimitException same to sync method
        '''
        with self.assertRaises(RateLimitException):
            limited_async = limits(calls=1, period=10, clock=clock)(async_func_to_test)
            await limited_async()
            await limited_async()

    async def _mock_sleep(self, *args, **kwargs):
        clock.increment()

    @pytest.mark.asyncio
    async def test_sleep_and_retry_async(self):
        period = 0.1
        sleep_mock = patch('ratelimit.decorators.asyncio.sleep').start()
        sleep_mock.side_effect = self._mock_sleep
        fun = sleep_and_retry(limits(calls=1, period=period, clock=clock)(async_func_to_test))
        self.assertTrue(inspect.iscoroutinefunction(fun))

        await fun()
        await fun()
        sleep_mock.assert_called_once_with(period)
