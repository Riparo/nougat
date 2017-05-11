import pytest
from misuzu.utils import *


def test_not_awaitable_middleware():
    with pytest.raises(UnknownMiddlewareException):
        def test_middleware(ctx, next):
            pass
        is_middleware(test_middleware)

def test_3_or_more_params():
    with pytest.raises(UnknownMiddlewareException):
        async def test_middleware(ctx, next, more):
            pass

        is_middleware(test_middleware)


def test_first_param_is_not_ctx():
    with pytest.raises(UnknownMiddlewareException):
        async def test_middleware(ctxx, next):
            pass

        is_middleware(test_middleware)


def test_second_param_is_not_next():
    with pytest.raises(UnknownMiddlewareException):
        async def test_middleware(ctx, nextt):
            pass

        is_middleware(test_middleware)