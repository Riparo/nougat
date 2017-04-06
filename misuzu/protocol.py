import asyncio
import httptools
from .request import Request
from .response import Response, json
from pprint import pprint
from time import time


class HttpProtocol(asyncio.Protocol):

    def __init__(self, router, loop):
        """
        :param router: Router Instance
        :param loop: uvloop or asyncio loop
        """
        self.loop = loop
        self.transport = None
        self.request = None
        self.parser = None
        self.url = None
        self.headers = None
        self.router = router
        self.__body = []

    def connection_made(self, transport):
        """
        asyncio.Protocol override 函数，当 Protocol 连接时调用
        :param transport:
        :return:
        """
        self.transport = transport

    def connection_lost(self, exc):
        """
        asyncio.Protocol override 函数，当 Protocol 失去连接时调用
        :param exc:
        :return:
        """
        self.request = self.parser = None
        self.__body = []

    # -------------------------------------------- #
    # Parsing
    # -------------------------------------------- #

    def data_received(self, data):
        """
        asyncio.Protocol override 函数，当 数据传入时调用
        :param data:
        :return:
        """

        if self.parser is None:
            self.headers = []
            self.parser = httptools.HttpRequestParser(self)

        # 传递信息至 HttpRequestParser 解析
        self.parser.feed_data(data)

    def on_url(self, url):
        """
        HttpRequestParser 解析函数
        :param url:
        :return:
        """
        self.url = url

    def on_header(self, key, value):
        """
        HttpRequestParser 解析函数
        :param key:
        :param value:
        :return:
        """
        self.headers.append((key.decode(), value.decode()))

    def on_headers_complete(self):
        """
        HttpRequestParser 解析函数
        :return:
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
        # 调用处理函数
        self.loop.create_task(self.process(self.request))
    # -------------------------------------------- #
    # Responding
    # -------------------------------------------- #

    # 处理函数
    async def process(self, request):
        """
        路由处理流程
                  request              request
        Middle ------------> Middle ------------> ... --->  Route
         Ware  <------------  ware  <------------ ... ---> Handler
                  response             response

        :param request:
        :return:
        """
        pprint("url {}".format(request.url.decode('utf-8')))

        route = self.router.get(request.url, request.method)
        request.generate_params(route.params)
        handler = route.handler
        
        if asyncio.iscoroutinefunction(handler):
            result = await handler(request)
        else:
            result = handler(request)
        
        # if not return Response's instance, then json it
        if not isinstance(result, Response):
            result = json(result)
        
        self.write_response(result)

    def write_response(self, response):
        """
        把 Response 类中的内容写入 self.transport 中
        :param response:
        :return:
        """
        self.transport.write(response.output(self.request.version))

        if not self.parser.should_keep_alive():
            self.transport.close()
        self.parser = None
        self.request = None
