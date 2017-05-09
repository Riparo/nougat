class Context(object):

    def __init__(self):
        self.url = None
        self.cookies = None
        self.headers = None
        self.params = None

        self.__version = None
        self.method = None
        self.query = None

    @property
    def content_type(self):
        return self.headers.get('CONTENT_TYPE', '').lower()

    def set_cookies(self, value):
        # TODO set cookies
        pass

    def set_secret_cookies(self, value):
        # TODO set secret cookies
        pass
