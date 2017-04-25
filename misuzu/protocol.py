import asyncio
import httptools
from .request import Request
from .response import Response, json
from .exceptions import HttpException
from pprint import pprint
from time import time


__all__ = ['HttpProtocol']


class HttpProtocol(asyncio.Protocol):

    def __init__(self, app, loop):
        """
        :param app: Misuzu Instance
        :param loop: uvloop or asyncio loop
        """
        self.app = app
        self.loop = loop
        self.transport = None
        self.request = None
        self.parser = None
        self.url = None
        self.headers = None
        self.router = self.app.router
        self.__body = []
        self.__middlewares = []

    def connection_made(self, transport):
        """
        asyncio.Protocol override 函数，当 Protocol 连接时调用
        """
        self.transport = transport

    def connection_lost(self, exc):
        """
        asyncio.Protocol override 函数，当 Protocol 失去连接时调用
        """
        self.request = self.parser = None
        self.__body = []

    def data_received(self, data):
        """
        asyncio.Protocol override 函数，当 数据传入时调用

        """

        if self.parser is None:
            self.headers = []
            self.parser = httptools.HttpRequestParser(self)

        # 传递信息至 HttpRequestParser 解析
        self.parser.feed_data(data)

    def on_url(self, url):
        """
        HttpRequestParser 解析函数
        """
        self.url = url

    def on_header(self, key, value):
        """
        HttpRequestParser 解析函数
        """
        self.headers.append((key.decode(), value.decode()))

    def on_headers_complete(self):
        """
        HttpRequestParser 解析函数
        """
        # 构建 Request 类
        url = httptools.parse_url(self.url)
        self.request = Request(
            url=url.path,
            headers=self.headers,
            version=self.parser.get_http_version(),
            method=self.parser.get_method(),
            query=url.query
        )

    def on_body(self, body):
        self.__body.append(body)

    def on_message_complete(self):

        self.request.init_body(b''.join(self.__body))

        # calling handler function
        handler_future = asyncio.Future()
        asyncio.ensure_future(self.app.handler(self.request, handler_future))
        handler_future.add_done_callback(self.on_response)

    def on_response(self, handler_future):

        response = handler_future.result()
        self.transport.write(response.output(self.request.version))

        if not self.parser.should_keep_alive():
            self.transport.close()
        self.parser = None
        self.request = None
