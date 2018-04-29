class HttpException(Exception):

    def __init__(self, code: int, body: str=''):
        super().__init__()
        self.body: str = body
        self.code: code = code


class UnknownMiddlewareException(Exception):

    def __init__(self, err: str):
        if err:
            self.err = err

    def __str__(self):
        return self.err


class UnknownSignalException(Exception):

    def __init__(self, name: str):
        self.name: str = name

    def __str__(self):
        return 'can not add signal {}'.format(self.name)
