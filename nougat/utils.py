import inspect
import json
from nougat.exceptions import UnknownMiddlewareException, ConfigException, ResponseContentCouldNotFormat
from cgi import parse_header


def is_middleware(func):
    """
    test whether it is a middleware
    :return: Boolean
    """
    args = list(inspect.signature(func).parameters.items())

    if not inspect.iscoroutinefunction(func):
        raise UnknownMiddlewareException("middleware {} should be awaitable".format(func.__name__))

    if len(args) != 2:
        raise UnknownMiddlewareException("middleware {} should has 2 params named context and next".format(func.__name__))

    if args[0][0] != 'context':
        raise UnknownMiddlewareException("the first param's name of middleware {} should be context".format(func.__name__))

    if args[1][0] != 'next':
        raise UnknownMiddlewareException("the second param's name of middleware {} should be next".format(func.__name__))


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


def parse_multipart(fp, pdict):
    """
    """
    import http.client
    maxlen = 0

    boundary = b""
    if 'boundary' in pdict:
        boundary = pdict['boundary']
    nextpart = b"--" + boundary
    lastpart = b"--" + boundary + b"--"
    partdict = {}
    terminator = b""

    while terminator != lastpart:
        bytes = -1
        data = None
        if terminator:
            # At start of next part.  Read headers first.
            headers = http.client.parse_headers(fp)
            clength = headers.get('content-length')
            if clength:
                try:
                    bytes = int(clength)
                except ValueError:
                    pass
            if bytes > 0:
                if maxlen and bytes > maxlen:
                    raise ValueError('Maximum content length exceeded')
                data = fp.read(bytes)
            else:
                data = b""
        # Read lines until end of part.
        lines = []
        for line in fp.split(b"\n"):
            if line.startswith(b"--"):
                terminator = line.rstrip()
                if terminator in (nextpart, lastpart):
                    break
            lines.append(line)
        else:
            terminator = lastpart

        # Done with part.
        if data is None:
            continue
        if bytes < 0:
            if lines:
                # Strip final line terminator
                line = lines[-1]
                if line[-2:] == b"\r\n":
                    line = line[:-2]
                elif line[-1:] == b"\n":
                    line = line[:-1]
                lines[-1] = line
                data = b"".join(lines)
        headers = http.client.parse_headers(fp)
        line = headers['content-disposition']
        if not line:
            continue
        key, params = parse_header(line)
        if key != 'form-data':
            continue
        if 'name' in params:
            name = params['name']
        else:
            continue
        if name in partdict:
            partdict[name].append(data)
        else:
            partdict[name] = [data]

    return partdict


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
    context.response.res = result


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
