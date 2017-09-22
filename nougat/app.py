import asyncio
import logging
import signal
import sys
import inspect
from contextlib import contextmanager
from functools import partial
from nougat.protocol import HttpProtocol
from nougat.test_client import TestClient
from nougat.section import Section
from nougat.exceptions import *
from nougat.utils import is_middleware
from nougat.config import Config

from typing import List, Tuple, TypeVar, Type, Set
from nougat.context import Request, Response
from nougat.routing import Routing, Route, Router

try:
    import uvloop
except:
    uvloop = asyncio

__all__ = ['Nougat']

RoutingType = TypeVar('RoutingType', bound=Routing)


class Nougat(object):

    def __init__(self, name='Nougat APP') -> None:

        self.name = name
        self.__test_client = None
        self.router: 'Router' = Router()

        self.config = Config()
        self.__middleware_chain = []

        self.sections = {}

        # new version
        self.__routes: Set[Tuple('Routing', 'Route')] = set()

    def use(self, middleware):
        """
        register middleware
        """

        is_middleware(middleware)
        middleware = middleware
        self.__middleware_chain.append(middleware)

    async def handler(self, request, handler_future):

        # try:
        #     # find route
        #     route = self.router.get(context)
        #     if not route:
        #         raise HttpException(None, 404)
        #
        #     section = self.sections.get(route.section_name)
        #     context.generate_params(route)
        #
        #     handler = partial(section.handler, context=context, route=route)
        #
        #     for middleware in self.chain:
        #         handler = partial(middleware, ctx=context, next=handler)
        #
        #     await handler()
        #
        # except HttpException as e:
        #
        #     context.status = e.status
        #     context.res = e.body
        #
        # handler_future.set_result(context)
        response = Response()

        try:

            routing, route = self.router.match(request.method,  request.url.path)
            routing = routing(request, response)
            controller_res = route.controller(routing)
        except RouteNoMatchException:
            response.status = 404
            controller_res = ''

        response.res = controller_res

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

    @contextmanager
    def create_server(self, loop, host="127.0.0.1", port=8000):

        server_coroutine = loop.create_server(partial(HttpProtocol, loop=loop, app=self), host, port)
        yield
        server_coroutine.close()

    def stop(self):
        asyncio.get_event_loop().stop()

    def doc(self):
        """
        generate the api document
        :return: 
        """
        return {
            'name': self.name,
            'sections': [section.doc() for _, section in self.sections.items()]
        }

    def route(self, routing: Type[RoutingType]):

        logging.info('adding Routing {}'.format(routing.__class__))

        routing_prefix = routing.prefix

        for route in routing.routes():
            route.route = "{}{}".format(routing_prefix, route.route)
            self.router.add_routing(routing, route)
