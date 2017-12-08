import inspect
import json
from nougat.exceptions import UnknownMiddlewareException, ResponseContentCouldNotFormat


def is_middleware(func):
    """
    test whether it is a middleware
    :return: Boolean
    """
    args = list(inspect.signature(func).parameters.items())

    # if not inspect.isawaitable(func):
    #     raise UnknownMiddlewareException("middleware {} should be awaitable".format(func.__name__))

    if len(args) != 3:
        raise UnknownMiddlewareException("middleware {} should has 3 params named req, res and next".format(func.__name__))

    if args[0][0] != 'req':
        raise UnknownMiddlewareException("the first param's name of middleware {} should be req".format(func.__name__))

    if args[1][0] != 'res':
        raise UnknownMiddlewareException("the second param's name of middleware {} should be res".format(func.__name__))

    if args[2][0] != 'next':
        raise UnknownMiddlewareException("the third param's name of middleware {} should be next".format(func.__name__))

    return True

def response_format(content):
    """
    format different type contents as str
    :return THE_TYPE_OF_CONTENT, CONTENT_FORMATTED
    """
    if isinstance(content, str):
        return "text/plain", content
    elif isinstance(content, list) or isinstance(content, dict):
        return "application/json", json.dumps(content)
    else:
        try:
            return "text/plain", str(content)
        except:
            raise ResponseContentCouldNotFormat()


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


async def controller_result_to_response(context, next):
    result = await next()
    context.response.content = result


async def empty():
    pass


class ConsoleColor:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def color_generator(color, text: str, bold: bool=False, underline: bool=False):

        origin: str = str(text)
        origin = color + origin + ConsoleColor.END
        if bold:
            origin = ConsoleColor.bold(origin)
        if underline:
            origin = ConsoleColor.UNDERLINE + origin + ConsoleColor.END

        return origin

    @staticmethod
    def blue(text: str, bold: bool=False, underline: bool=False):
        return ConsoleColor.color_generator(ConsoleColor.BLUE, text, bold, underline)

    @staticmethod
    def purple(text: str, bold: bool=False, underline: bool=False):
        return ConsoleColor.color_generator(ConsoleColor.PURPLE, text, bold, underline)

    @staticmethod
    def green(text: str, bold: bool=False, underline: bool=False):
        return ConsoleColor.color_generator(ConsoleColor.GREEN, text, bold, underline)

    @staticmethod
    def yellow(text: str, bold: bool=False, underline: bool=False):
        return ConsoleColor.color_generator(ConsoleColor.YELLOW, text, bold, underline)

    @staticmethod
    def red(text: str, bold: bool=False, underline: bool=False):
        return ConsoleColor.color_generator(ConsoleColor.RED, text, bold, underline)

    @staticmethod
    def bold(text: str):
        return ConsoleColor.BOLD + text + ConsoleColor.END


class File:

    def __init__(self, name, data):
        self.name = name
        self.data = data

    def __str__(self):
        return '<File {}>'.format(self.name)

    def __repr__(self):
        return '<File {}>'.format(self.name)
