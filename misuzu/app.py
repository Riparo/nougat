import asyncio
import logging
from .router import Router, Param
from .protocol import HttpProtocol
from .test_client import TestClient
from .middleware import BaseMiddleware
from .section import Section
from .exceptions import *
from .response import json

try:
    import uvloop
except:
    uvloop = asyncio

__version__ = "0.0.2"


class Misuzu(object):

    def __init__(self, name):
        """
        初始化 Misuzu 类
        :param name: APP 名称， 并没有什么用
        """
        self.name = name
        self.__test_client = None
        self.router = Router()
        self.chains = []

        self.sections = []
        self.__sections_name = []

        self.__temper_params = []

    def run(self, host="127.0.0.1", port=8000, debug=False, loop=None):
        # Create Event Loop
        loop = loop or uvloop.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.set_debug(debug)

        if debug:
            logging.basicConfig(level=logging.DEBUG)

        server_coroutine = loop.create_server(lambda: HttpProtocol(loop=loop, app=self), host, port)
        server_loop = loop.run_until_complete(server_coroutine)
        try:
            print("run forever")
            loop.run_forever()
        except KeyboardInterrupt:
            print("ctrl+c")
            server_loop.close()
            loop.close()

    def stop(self):
        asyncio.get_event_loop().stop()

    @property
    def test(self):
        if not self.__test_client:
            return TestClient(self)
        return self.__test_client

    def register_middleware(self, middleware):
        """
        注册 Middleware
        :param middleware:
        :return:
        """
        if BaseMiddleware not in middleware.__bases__:
            raise UnknownMiddlewareException()

        self.chains.append(middleware)

    def register_section(self, section):
        if not isinstance(section, Section):
            raise UnknownSectionException()

        if section.name in self.__sections_name:
            raise MisuzuRuntimeError("it seems that this section's name had beed registered")

        logging.debug("register section {}".format(section.name))
        self.sections.append(section)
        self.__sections_name.append(section.name)

        # TODO add router

    async def handler(self, request, handler_future):

        result = json({"hello": "hello"})
        handler_future.set_result(result)
