class HttpException(Exception):

    def __init__(self, status, body):
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


class RouteNoMatchException(Exception):
    pass


class ParamRedefineException(Exception):

    def __init__(self, rule: str, name: str) -> None:
        self.rule = rule
        self.name = name

    def __str__(self) -> str:
        return "{} seems redefine param named {}".format(self.rule, self.name)


class ResponseContentCouldNotFormat(Exception):

    def __str__(self):
        return "the content of rescponse could not be formatted as str"


class ParamNeedDefaultValueIfItsOptional(Exception):
    pass


class ParamComingFromUnknownLocation(Exception):

    def __init__(self, name, unexpected_location):
        self.name = name
        self.unexpected_location = unexpected_location

    def __str__(self):
        return "Parameter {} could not be loaded from localtion {}".format(self.name, self.unexpected_location)


class ParamCouldNotBeFormattedToTargetType(Exception):

    def __init__(self, target_type: str, info: str=None):
        self.target_type = target_type
        self.info = info or ''
