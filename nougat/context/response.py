
class Response:

    def __init__(self, status: int=200):

        self.__version = '1.1'
        self.status = status

        self.content = ''
        self.type = 'text/html'
        self.charset = 'utf-8'

        self.headers = {}
        self.__body = None

    @property
    def output(self):
        """
        output the http payload
        """
        return self.__body.encode(self.charset)

    def output_generator(self):
        """
        generate the http response headers and body
        if output method is called without calling it, the response is always None
        :return:
        """

        self.__body = self.content or ''
        self.set_header('Content-Type', "{};charset={}".format(self.type, self.charset))
        self.set_header('Content-Length', '{}'.format(len(self.__body.encode(self.charset))))

    def set_header(self, key, value):
        """
        set response header
        :param key: the key of header
        :param value: the value of header
        """
        self.headers[key] = value

    def set_cookies(self, name, value, expires=None, domain=None, path=None, secure=False, http_only=False,
                    same_site=None):
        """

        :param name: cookies name
        :param value: cookies value
        :param expires: number of seconds until the cookie expires
        :param domain: specifies those hosts to which the cookie will be sent
        :param path: indicates a URL path that must exist in the requested resource before sending the Cookie header
        :param secure: a secure cookie will only be sent to the server when a request is made using SSL and the HTTPS protocol
        :param http_only:
        :param same_site:
        :return:
        """

        header_value = "{}={}".format(name, value)

        if expires:
            header_value = "{}; Max-Age={}".format(header_value, expires)
        if domain:
            header_value = "{}; Domain={}".format(header_value, domain)
        if path:
            header_value = "{}; Path={}".format(header_value, path)
        if secure:
            header_value = "{}; Secure".format(header_value)
        if http_only:
            header_value = "{}; HttpOnly".format(header_value)
        if same_site:
            header_value = "{}; SameSite={}".format(header_value, same_site)

        self.set_header("Set-Cookie", header_value)

    @property
    def header_as_list(self):
        return [(key, value) for key, value in self.headers.items()]
