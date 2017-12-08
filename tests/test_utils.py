import pytest
from nougat.utils import *


def test_not_awaitable_middleware():
    with pytest.raises(UnknownMiddlewareException):
        def test_middleware(context, next):
            pass
        is_middleware(test_middleware)


def test_3_or_more_params():
    with pytest.raises(UnknownMiddlewareException):
        async def test_middleware(context, next, more):
            pass

        is_middleware(test_middleware)


def test_first_param_is_not_ctx():
    with pytest.raises(UnknownMiddlewareException):
        async def test_middleware(ctxx, next):
            pass

        is_middleware(test_middleware)


def test_second_param_is_not_next():
    with pytest.raises(UnknownMiddlewareException):
        async def test_middleware(context, nextt):
            pass

        is_middleware(test_middleware)


def test_use_pass_middleware():

    async def test(req, res, next):
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


def test_terminal_color_text():

    assert ConsoleColor.blue('123') == '\033[94m123\033[0m'
    assert ConsoleColor.purple('123') == '\033[95m123\033[0m'
    assert ConsoleColor.green('123') == '\033[92m123\033[0m'
    assert ConsoleColor.yellow('123') == '\033[93m123\033[0m'
    assert ConsoleColor.red('123') == '\033[91m123\033[0m'
    assert ConsoleColor.bold('123') == '\033[1m123\033[0m'

    assert ConsoleColor.blue('123', bold=True, underline=True) == '\033[4m\033[1m\033[94m123\033[0m\033[0m\033[0m'
