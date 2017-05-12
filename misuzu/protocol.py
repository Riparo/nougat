import asyncio
import httptools
from misuzu.context import Context

__all__ = ['HttpProtocol']


class HttpProtocol(asyncio.Protocol):

    def __init__(self, app, loop):
        """
        :param app: Misuzu Instance
        :param loop: uvloop or asyncio loop
        """
        self.app = app
        self.loop = loop

        self.path = None
        self.headers = None

        self.context = None

        self.transport = None
        self.parser = None

        self.__body = []

    def connection_made(self, transport):
        """
        asyncio.Protocol override 函数，当 Protocol 连接时调用
        """
        self.transport = transport

    def connection_lost(self, exc):
        """
        asyncio.Protocol override 函数，当 Protocol 失去连接时调用
        """
        self.context = None
        self.parser = None
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
        self.path = url

    def on_header(self, key, value):
        """
        HttpRequestParser 解析函数
        """
        self.headers.append((key.decode(), value.decode()))

    def on_headers_complete(self):
        """
        HttpRequestParser 解析函数
        """
        # 构建 Context 类
        self.context = Context(
            app=self.app,
            path=self.path,
            headers=self.headers,
            version=self.parser.get_http_version(),
            method=self.parser.get_method().decode('utf-8'),
        )

    def on_body(self, body):
        self.__body.append(body)

    def on_message_complete(self):

        self.context.init_body(b''.join(self.__body))

        # calling handler function
        handler_future = asyncio.Future()
        asyncio.ensure_future(self.app.handler(self.context, handler_future))
        handler_future.add_done_callback(self.on_response)

    def on_response(self, handler_future):

        response = handler_future.result()
        self.transport.write(response.output)

        if not self.parser.should_keep_alive():
            self.transport.close()
        self.parser = None
        self.context = None
