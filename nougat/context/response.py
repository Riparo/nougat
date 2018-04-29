from typing import Dict, List, Tuple, Optional


class Response:

    def __init__(self, code: int=200, status: Optional[str]=None):

        self.__version = '1.1'
        self.code: int = code
        self.status: str = status

        self.content: str = ''
        self.type: str = 'text/html'
        self.charset: str = 'utf-8'

        self.headers: Dict[str, str] = {}
        self.cookies: Dict[str, str] = {}

    @property
    def output(self) -> bytes:
        """
        encode content into target charset
        """
        return self.content.encode(self.charset)

    def set_header(self, key: str, value: str) -> None:
        """
        set response header
        :param key: the key of header
        :param value: the value of header
        """
        self.headers[key] = value

    def set_cookies(self,
                    name: str,
                    value: str,
                    expires: Optional[int]=None,
                    domain: Optional[str]=None,
                    path: Optional[str]=None,
                    secure: bool=False,
                    http_only: bool=False,
                    same_site: Optional[str]=None) -> None:
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

        cookie: str = value

        if expires:
            cookie = "{}; Max-Age={}".format(cookie, expires)
        if domain:
            cookie = "{}; Domain={}".format(cookie, domain)
        if path:
            cookie = "{}; Path={}".format(cookie, path)
        if secure:
            cookie = "{}; Secure".format(cookie)
        if http_only:
            cookie = "{}; HttpOnly".format(cookie)
        if same_site:
            cookie = "{}; SameSite={}".format(cookie, same_site)

        self.cookies[name] = cookie

    @property
    def header_as_list(self) -> List[Tuple[str, str]]:

        _headers: List[Tuple[str, str]] = list()

        _headers.append(('Content-Type', "{};charset={}".format(self.type, self.charset)))
        _headers.append(('Content-Length', str(len(self.output))))

        for key, value in self.headers.items():
            _headers.append((key, value))
        for key, value in self.cookies.items():
            _headers.append(('Set-Cookie', '{}={}'.format(key, value)))

        return _headers
