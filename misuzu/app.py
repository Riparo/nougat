import asyncio
import logging
import signal
from functools import partial
from .router import Router, Param
from .protocol import HttpProtocol
from .test_client import TestClient
from .middleware import BaseMiddleware
from .section import Section
from .exceptions import *
from .response import json, Response

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
        self.router = Router(self.name)
        self.chains = []

        self.sections = {}

        self.__temper_params = []

    def run(self, host="127.0.0.1", port=8000, debug=False, loop=None):
        # Create Event Loop
        loop = loop or uvloop.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.set_debug(debug)

        if debug:
            logging.basicConfig(level=logging.DEBUG)

        def ask_exit():
            loop.stop()

        for signame in ('SIGINT', 'SIGTERM'):
            loop.add_signal_handler(getattr(signal, signame), ask_exit)

        server_coroutine = loop.create_server(partial(HttpProtocol, loop=loop, app=self), host, port)
        server_loop = loop.run_until_complete(server_coroutine)
        try:
            print("server http://{}:{} is running, press Ctrl+C to interrupt.".format(host, port))
            loop.run_forever()
        finally:
            server_coroutine.close()
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

        if section.name in self.sections:
            raise MisuzuRuntimeError("it seems that this section's name had been registered")

        logging.debug("register section {}".format(section.name))
        self.sections[section.name] = section

        # TODO add router
        self.router.union(section.router)

    async def handler(self, request, handler_future):

        temp_middlewares= []

        # find route
        route = self.router.get(request.url, request.method)
        section = self.sections.get(route.section_name)
        request.generate_params(route)

        try:
            # Request Middleware
            for middleware in self.chains:
                temp = middleware()
                temp_middlewares.append(temp)
                temp.on_request(request)

            if section:
                response = await section.handler(request, route)
            else:
                response = await route.handler(request)

            # if not return Response's instance, then json it
            if not isinstance(response, Response):
                response = json(response)

            # Response Middleware
            temp_middlewares.reverse()
            for middleware in temp_middlewares:
                middleware.on_response(response)

        except HttpException as e:

            response = Response(e.body, e.status)

        # TODO Redirect

        handler_future.set_result(response)
