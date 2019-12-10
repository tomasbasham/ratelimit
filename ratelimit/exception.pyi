from typing import Text


class RateLimitException(Exception):
    period_remaining: float

    def __init__(self, message: Text, period_remaining: float) -> None: ...
