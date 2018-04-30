import inspect
from functools import partial
from nougat.exceptions import UnknownMiddlewareException

from typing import Callable, Awaitable, TYPE_CHECKING

if TYPE_CHECKING:
    from nougat import Nougat
    from nougat.context import Request, Response

MiddlewareType = Callable[..., Awaitable[None]]

MIDDLEWARE_PARAMETER_BOUNDARY = {'app', 'request', 'response', 'next'}


def is_middleware(func) -> bool:
    """
    test whether it is a middleware
    :return: Boolean
    """

    if inspect.isfunction(func):
        _check = func
        _name = func.__name__
    else:
        _check = func.__call__
        _name = func.__class__.__name__

    if not inspect.iscoroutinefunction(_check):
        raise UnknownMiddlewareException("Middleware {} should be async function".format(_name))

    args = list(inspect.signature(_check).parameters.keys())

    if set(args) - MIDDLEWARE_PARAMETER_BOUNDARY:
        raise UnknownMiddlewareException("Parameters of middleware {} "
                                         "must be in list ['app', 'request', 'response', 'next']".format(_name))

    return True


def map_context_to_middleware(middleware: MiddlewareType,
                              app: 'Nougat',
                              request: 'Request',
                              response: 'Response',
                              next: Callable[[], Awaitable[None]]) -> Callable[[], Awaitable[None]]:
    all_mapping = {
        'app': app,
        'request': request,
        'response': response,
        'next': next
    }
    args = list(inspect.signature(middleware).parameters.keys())
    current_mapping = {key: all_mapping[key] for key in args}

    return partial(middleware, **current_mapping)


async def empty():
    pass


class cached_property(object):
    """
    A property that is only computed once per instance and then replaces itself
    with an ordinary attribute. Deleting the attribute resets the property.
    Source: https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
    """

    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


class File:

    def __init__(self, name, data):
        self.name = name
        self.data = data

