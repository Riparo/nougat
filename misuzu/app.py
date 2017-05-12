import asyncio
import logging
import signal
import sys
import inspect
from functools import partial
from misuzu.router import Router, Param
from misuzu.protocol import HttpProtocol
from misuzu.test_client import TestClient
from misuzu.section import Section
from misuzu.exceptions import *
from misuzu.response import json, Response
from misuzu.utils import is_middleware

try:
    import uvloop
except:
    uvloop = asyncio

__all__ = ['Misuzu']


class Misuzu(object):

    __slots__ = ['name', '__test_client', 'router', 'chains', 'sections']

    def __init__(self, name=None):
        """
        初始化 Misuzu 类
        :param name: APP 名称， 并没有什么用
        """
        self.name = name
        self.__test_client = None
        self.router = Router(self.name)
        self.chains = []

        self.sections = {}

    def use(self, middleware_or_section_name):
        if isinstance(middleware_or_section_name, Section):
            section = middleware_or_section_name
            if section.name in self.sections:
                raise MisuzuRuntimeError("it seems that this section's name had been registered")
            logging.debug("register section {}".format(section.name))
            self.sections[section.name] = section

            self.router.union(section.router)
        elif inspect.isfunction(middleware_or_section_name):
                is_middleware(middleware_or_section_name)
                middleware = middleware_or_section_name
                self.chains.append(middleware)
        else:
            raise MisuzuRuntimeError("misuzu only can use section instance or middleware function")

    async def handler(self, context, handler_future):

        # TODO code factor
        middleware_runtime_chains = []

        # find route
        route = self.router.get(context)
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

    @property
    def test(self):
        if not self.__test_client:
            return TestClient(self)
        return self.__test_client

    def run(self, host="127.0.0.1", port=8000, debug=False, loop=None):
        # Create Event Loop
        loop = loop or uvloop.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.set_debug(debug)

        if debug:
            logging.basicConfig(level=logging.DEBUG)

        def ask_exit():
            loop.stop()

        if sys.platform != 'win32':
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
