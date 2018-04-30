import json
import io
from yarl import URL
from urllib.parse import parse_qs
from cgi import parse_header, FieldStorage
from http.cookies import SimpleCookie

from nougat.utils import cached_property, File

from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from nougat.asgi import HTTPParser


class Request:

    def __init__(self, url: str, headers: Dict[str, str], ip: str, version: str, method: str, body: bytes):

        self.headers = headers
        self.method = method
        self.version = version
        self.form = {}
        self.ip = ip
        self.url = URL(url)

        self.__json = None
        self.raw_body = body

        self.__body_format(self.raw_body)

    @cached_property
    def content_type(self):
        return self.headers.get('Content-Type', '')

    @property
    def query(self):
        return self.url.query

    @cached_property
    def cookies(self):
        _cookies = {}
        cookies = SimpleCookie(self.headers.get('Cookie', ''))
        for cookie in cookies.values():
            _cookies[cookie.key] = cookie.value

        return _cookies

    def __body_format(self, body):
        """
        format body into different type
        :param body:
        :return:
        """

        ctype, pdict = parse_header(self.content_type)
        if ctype == 'application/json':
            self.form = json.loads(body.decode())

        elif ctype == 'application/x-www-form-urlencoded':
            for key, value in parse_qs(body).items():
                    self.form[key.decode()] = [one_value.decode() for one_value in value]

        elif ctype == "multipart/form-data":
            safe_env = {
                'QUERY_STRING': '',
                'REQUEST_METHOD': self.method.upper(),
                'CONTENT_TYPE': self.content_type,
                'CONTENT_LENGTH': self.headers.get('Content-Length', '-1')
            }
            fields = FieldStorage(io.BytesIO(body), environ=safe_env, keep_blank_values=True)

            fields = fields.list or []
            for field in fields:
                if field.filename:
                    self.form[field.name] = File(field.filename, field.file)
                else:
                    self.form[field.name] = field.value

    @staticmethod
    def load_from_parser(parser: 'HTTPParser') -> 'Request':

        return Request(
            url=parser.url,
            headers=parser.headers,
            ip=parser.raw_ip,
            version=parser.version,
            method=parser.method.decode().upper(),
            body=parser.body
        )
