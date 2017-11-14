import logging
from functools import partial
from nougat.exceptions import *
from nougat.utils import is_middleware, controller_result_to_response
from nougat.config import Config

from typing import List, Tuple, TypeVar, Type, Set, Union, Callable
from nougat.context import Request, Response
from nougat.routing import Routing, Route, Router

from nougat.http_wrapper import HTTPWrapper
import asyncio


RoutingType = TypeVar('RoutingType', bound=Routing)


class Nougat(object):

    def __init__(self, name='Nougat APP') -> None:

        self.name = name
        self.router: 'Router' = Router()

        self.config = Config()
        self.__middleware_chain = []

        self.sections = {}


        self.debug: bool = False

        # new version
        self.__routes: Set[Tuple('Routing', 'Route')] = set()

    def use(self, middleware):
        """
        Register Middleware
        :param middleware: The Middleware Function
        """

        is_middleware(middleware)
        middleware = middleware
        self.__middleware_chain.append(middleware)

    async def handler(self, request: 'Request'):
        """
        The handler handling each request
        :param request: the Request instance
        :return: The Response instance
        """

        response = Response()

        try:

            # match the Routing and Route from Router
            routing_class, route, url_dict = self.router.match(request.method, request.url.path)
            request.url_dict = url_dict
            routing = routing_class(self, request, response, route)

            # Handling Middleware
            handler = partial(route.controller, routing)

            # save the return value to response.res
            handler = partial(controller_result_to_response, context=routing, next=handler)  # save the result to response res

            # Routing Time
            handler = await routing.handler(route, handler)

            # Global Middleware
            chain_reverse = self.__middleware_chain[::-1]
            for middleware in chain_reverse:
                handler = partial(middleware, context=routing, next=handler)

            await handler()

            # Formatting the Response data

        except ResponseContentCouldNotFormat:
            response.type = 'text/plain'
            response.res = "unable to format response"

        except RouteNoMatchException:
            response.status = 404
            response.type = 'text/plain'
            response.res = None

        except HttpException as e:
            response.status = e.status
            response.res = e.body

        return response

    def run(self, host: str="localhost", port: int=8000, debug: bool=False):
        """
        start the http server
        :param host: The listening host
        :param port: The listening port
        :param debug: whether it is in debug mod or not
        :return:
        """
        if debug:
            print("Nougat is listening on http://{}:{}\n".format(host, port))
        self.debug = debug
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.start_server(host, port))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            loop.close()

    def doc(self):
        """
        generate the api document
        :return: the json of api structure
        """
        return {
            'name': self.name,
            'sections': [section.doc() for _, section in self.sections.items()]
        }

    def route(self, routing: Type[RoutingType]):
        """
        Register Routing class
        :param routing: Routing Class, not its instance
        :return:
        """
        logging.info('adding Routing {}'.format(routing.__class__))

        routing_prefix = routing.prefix

        for route in routing.routes():
            route.set_prefix(routing_prefix)
            self.router.add_routing(routing, route)

    async def start_server(self, host: str, port: int):

        return await asyncio.start_server(self.http_serve, host, port)

    async def http_serve(self, reader, writer):
        """
        the income function of curio.tcp_server
        """
        address = writer.get_extra_info('peername')
        await HTTPWrapper((reader, writer), address).process(self)
