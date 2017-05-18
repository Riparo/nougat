class HttpException(Exception):

    def __init__(self, body, status):
        super().__init__()
        self.body = body
        self.status = status


class UnknownMiddlewareException(Exception):

    def __init__(self, err=None):
        if err:
            self.err = err
        else:
            self.err = 'Unknown middleware exception'

    def __str__(self):
        return self.err


class UnknownSectionException(Exception): pass


class UnknownRouterException(Exception): pass


class RouteReDefineException(Exception):

    def __init__(self, method, url):
        self.method = method
        self.url = url

    def __str__(self):
        return "{} {} seems been redefined".format(self.method, self.url)


class MisuzuRuntimeError(Exception):

    def __init__(self, text=""):
        self.text = text