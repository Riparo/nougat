import logging
from functools import partial
from nougat.exceptions import *
from nougat.utils import is_middleware, response_format
from nougat.config import Config

from typing import List, Tuple, TypeVar, Type, Set, Union, Callable
from nougat.context import Request, Response
from nougat.routing import Routing, Route, Router

from nougat.guarder import GuarderManager

import curio

from nougat.http_wrapper import HTTPWrapper


RoutingType = TypeVar('RoutingType', bound=Routing)


class Nougat(object):

    def __init__(self, name='Nougat APP') -> None:

        self.name = name
        self.router: 'Router' = Router()

        self.config = Config()
        self.__middleware_chain = []

        self.sections = {}

        self.guarder = GuarderManager()  # Guarder Manager
        self.guarder.guard(self, 'app')

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

    def guarders(self, guarders: Union[List[Callable], Callable]):
        """
        Register Guarder function
        :param guarders: The Guarder Function
        """

        if not isinstance(guarders, list):
            guarders = [guarders]

        for guarder in guarders:
            # TODO: check redefinition
            self.guarder.guard(guarder)

    async def handler(self, request: 'Request'):
        """
        The handler handling each request
        :param request: the Request instance
        :return: The Response instance
        """

        response = Response()

        try:

            # match the Routing and Route from Router
            routing_class, route = self.router.match(request.method, request.url.path)
            routing = routing_class(request, response)

            # Guarder Processes
            with self.guarder.guard_context(routing):
                controller = await self.guarder.generator(route.controller)

            # Handling Middleware
            handler = partial(controller, routing)

            chain_reverse = self.__middleware_chain[::-1]
            for middleware in chain_reverse:
                handler = partial(middleware, context=routing, next=handler)

            controller_res = await handler()

            # Formatting the Response data
            res_type, controller_res = response_format(controller_res)

        except ResponseContentCouldNotFormat:
            res_type = 'text/plain'
            controller_res = "unable to format response"

        except RouteNoMatchException:
            response.status = 404
            res_type = 'text/plain'
            controller_res = None

        response.type = res_type
        response.res = controller_res

        return response

    def run(self, host: str="localhost", port: int=8000, debug: bool=False):
        """
        start the http server
        :param host: The listening host
        :param port: The listening port
        :param debug: whether it is in debug mod or not
        :return:
        """

        print("Nougat is listening on http://{}:{}".format(host, port))
        curio.run(curio.tcp_server, host, port, self.http_serve)

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
            route.route = "{}{}".format(routing_prefix, route.route)
            self.router.add_routing(routing, route)

    async def http_serve(self, sock, address):
        """
        the income function of curio.tcp_server
        """
        await HTTPWrapper(sock, address).process(self)
