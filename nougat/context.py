import json
from yarl import URL
from urllib.parse import parse_qs
from cgi import parse_header, FieldStorage
from nougat.httpstatus import STATUS_CODES
from nougat.utils import cached_property, File
from typing import TYPE_CHECKING, Dict
import io

if TYPE_CHECKING:
    from nougat.app import Nougat

__all__ = ['Request', 'Response']


class Request:

    def __init__(self, app: 'Nougat', path: str, headers: Dict[str, str], ip: str, version: str, method: str, body: bytes):

        self.app = app
        self.__headers = headers
        self.method = method
        self.version = version
        self.__form = {}
        self.__original_ip = ip
        self.url = URL(path)

        self.url_dict = {}

        self.__json = None
        self.__raw_body = body
        self.req_body = self.__raw_body
        self.__is_format = False

    @cached_property
    def content_type(self):
        return self.headers.get('content-type', '').lower()

    @property
    def query(self):
        return self.url.query

    @cached_property
    def form(self):
        self.body_formator(self.__raw_body)
        return self.__form

    @cached_property
    def ip(self):
        if self.app.config.get("X_FORWARD_IP", False):
            return self.headers.get("X-Forwarded-For", "").strip().split(",")
        else:
            return self.__original_ip

    @cached_property
    def headers(self):
        return self.__headers

    @cached_property
    def cookies(self):
        cookies_format = {}
        _cookies = self.headers.get("Cookie", None) or self.headers.get("cookie", None)
        if _cookies:
            _cookies = _cookies.split("; ")
            for one_cookies in _cookies:
                if one_cookies != "":
                    one_cookies = one_cookies.split("=")
                    cookies_format[one_cookies[0]] = "=".join(one_cookies[1:])
        return cookies_format

    def body_formator(self, body):
        """
        format body into different type
        :param body:
        :return:
        """
        if not self.__is_format:
            self.__is_format = True
            # parse body as json
            ctype, pdict = parse_header(self.content_type)
            if ctype == 'application/json':
                self.__form = json.loads(body.decode())

            elif ctype == 'application/x-www-form-urlencoded':
                for key, value in parse_qs(body).items():
                        self.__form[key.decode()] = [one_value.decode() for one_value in value]

            elif ctype == "multipart/form-data":

                safe_env = {
                    'QUERY_STRING': '',
                    'REQUEST_METHOD': self.method.upper(),
                    'CONTENT_TYPE': self.content_type,
                    'CONTENT_LENGTH': self.headers.get('content-length', '-1')
                }
                fields = FieldStorage(io.BytesIO(body), environ=safe_env, keep_blank_values=True)

                fields = fields.list or []
                for field in fields:
                    if field.filename:
                        self.__form[field.name] = File(field.filename, field.file)
                    else:
                        self.__form[field.name] = field.value

            else:
                self.req_body = body


class Response:

    def __init__(self, status: int=200):

        self.__version = '1.1'
        self.status = status

        self.content = ''
        self.type = 'text/html'
        self.charset = 'utf-8'

        self.__headers = {}
        self.__body = ''

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
        self.set_header('Content-Length', '{}'.format(len(self.__body)))

    def set_header(self, key, value):
        """
        set response header
        :param key: the key of header
        :param value: the value of header
        """
        self.__headers[key] = value

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
        return [(key, value) for key, value in self.__headers.items()]
