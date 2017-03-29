
STATUS_CODES = {
    200: 'OK',
    404: 'Not Found'
}


class Config(dict):

    def __init__(self, default=None):
        super().__init__(default or {})

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError as e:
            raise AttributeError("{} do not exist".format(e.args[0]))

    def __setattr__(self, key, value):
        self[key] = value

    # TODO load config from file and object


