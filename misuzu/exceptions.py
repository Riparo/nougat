class HttpException(Exception):

    def __init__(self, body, status):
        super().__init__()
        self.body = body
        self.status = status


class UnknownMiddlewareException(Exception): pass


class UnknownSectionException(Exception): pass


class MisuzuRuntimeError(Exception):

    def __init__(self, text=""):
        self.text = text