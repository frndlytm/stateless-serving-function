import functools
import time

from typing import Callable

import flask

FlaskEndpoint = Callable[[flask.Request], flask.typing.ResponseReturnValue]


class assert_http_method:
    def __init__(self, methods: list[str] = []):
        self.methods = methods

    def __call__(self, func: FlaskEndpoint):
        @functools.wraps(func)
        def wrapper(request: flask.Request):
            if not request.method in self.methods:
                return "Method not allowed", 405
            return func(request)

        return wrapper


def timed(func):
    """timefunc's doc"""

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        """time_wrapper's doc string"""
        start = time.perf_counter()
        result = func(*args, **kwargs)
        time_elapsed = time.perf_counter() - start
        print(f"Function: {func.__name__}, Time: {time_elapsed}")
        return result

    return wrapped
