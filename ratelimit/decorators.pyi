import threading
from typing import Callable, TypeVar

from ratelimit.utils import CLOCK_FUNC, now

_RT = TypeVar('_RT')


class RateLimitDecorator(object):
    clamped_calls: int
    period: float
    clock: CLOCK_FUNC
    raise_on_limit: bool
    last_reset: float
    num_calls: int
    lock: threading.RLock

    def __init__(
            self,
            calls: int = 15,
            period: float = 900,
            clock: CLOCK_FUNC = now(),
            raise_on_limit: bool = True
    ) -> None:
        ...

    def __call__(self, func: Callable[..., _RT]) -> Callable[..., _RT]:
        ...

    def __period_remaining(self) -> float:
        ...


def sleep_and_retry(func: Callable[..., _RT]) -> Callable[..., _RT]:
    ...
