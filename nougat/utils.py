import inspect
import json
from nougat.exceptions import UnknownMiddlewareException, ConfigException, ResponseContentCouldNotFormat


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


def is_env_format(match, dict):
    """
    test whether it conform the standard
    :return: Boolean
    """
    if not match.group('name').isupper():
        raise ConfigException("<name>'{}' is not capitalized.".format(match.group('name')))

    if not match.group('type') in dict:
        raise ConfigException("<type>'{}' is out of list {}".format(match.group('type'), dict.keys()))


def response_format(content):
    """
    format different type contents as str
    """
    if isinstance(content, str):
        return "str", content
    elif isinstance(content, list) or isinstance(content, dict):
        return "json", json.dumps(content)
    else:
        try:
            return "str", str(content)
        except:
            raise ResponseContentCouldNotFormat()
