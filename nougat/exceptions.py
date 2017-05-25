class HttpException(Exception):

    def __init__(self, body, status):
        super().__init__()
        self.body = body
        self.status = status


class ConfigException(Exception):

    def __init__(self, err=None):
        if err:
            self.err = err
        else:
            self.err = 'Config is nonstandard'

    def __str__(self):
        return "Format : 'ENV::<name>::<type>::<default_value>'\n" + self.err


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


class NougatRuntimeError(Exception):

    def __init__(self, text=""):
        self.text = text


class HandlerRedefineException(Exception):

    def __init__(self, section, handler):
        self.section =section
        self.handler = handler

    def __str__(self):
        return "{} handler seems redefine in section {}".format(self.handler, self.section)


class ParamRedefineException(Exception):

    def __init__(self, rule, name):
        self.rule = rule
        self.name = name

    def __str__(self):
        return "{} seems redefine param named {}".format(self.rule, self.name)


class ParamMissingException(Exception):

    def __init__(self, rule, name):
        self.rule = rule
        self.name = name

    def __str__(self):
        return "{} seems miss param named {}".format(self.rule, self.name)
