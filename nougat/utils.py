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


class CachedProperty(object):
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
