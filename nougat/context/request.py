import json
import io
from yarl import URL
from urllib.parse import parse_qs
from cgi import parse_header, FieldStorage

from nougat.utils import cached_property, File

from typing import TYPE_CHECKING, Dict


class Request:

    def __init__(self, app, url: str, headers: Dict[str, str], ip: str, version: str, method: str, body: bytes):

        self.app = app
        self.__headers = headers
        self.method = method
        self.version = version
        self.__form = {}
        self.__original_ip = ip
        self.url = URL(url)

        self.url_dict = {}

        self.__json = None
        self.__raw_body = body
        self.req_body = self.__raw_body
        self.__is_format = False

    @cached_property
    def content_type(self):
        return self.headers.get('Content-Type', '').lower()

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

    @staticmethod
    def create_from_dict(app, request_dict: Dict):
        headers = dict(request_dict['headers'])
        return Request(
            app=app,
            url=request_dict['url'],
            headers=headers,
            ip=request_dict['ip'],
            version=request_dict['version'],
            method=request_dict['method'].decode().upper(),
            body=request_dict['body']
        )
