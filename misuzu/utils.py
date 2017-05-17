import inspect
from misuzu.exceptions import UnknownMiddlewareException


def is_middleware(func):
    """
    test whether it is a middleware
    :return: Boolean
    """
    args = list(inspect.signature(func).parameters.items())

    if not inspect.iscoroutinefunction(func):
        print("hello")
        raise UnknownMiddlewareException("middleware {} should be awaitable".format(func.__name__))

    if len(args) != 2:
        raise UnknownMiddlewareException("middleware {} should has 2 params named ctx and next".format(func.__name__))

    if args[0][0] != 'ctx':
        raise UnknownMiddlewareException("the first param's name of middleware {} should be ctx".format(func.__name__))

    if args[1][0] != 'next':
        raise UnknownMiddlewareException("the second param's name of middleware {} should be next".format(func.__name__))
