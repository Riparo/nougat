import pytest
import json
from nougat.utils import *


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


def test_use_pass_middleware():

    async def test(ctx, next):
        pass

    is_middleware(test)


def test_format_str():
    assert "str", "123" == response_format("123")


def test_format_list():
    assert "json", json.dumps([1, 2, 3]) == response_format([1, 2, 3])


def test_format_dict():
    assert "json", json.dumps({"hello": "world"}) == response_format({"hello": "world"})


def test_format_int():
    assert "str", "123" == response_format(123)
