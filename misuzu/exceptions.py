class HttpException(Exception):

    def __init__(self, body, status):
        super().__init__()
        self.body = body
        self.status = status


class UnknownMiddlewareException(Exception): pass
