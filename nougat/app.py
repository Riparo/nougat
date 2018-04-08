import logging
from functools import partial
from nougat.asgi import serve
from nougat.asgi.httpstatus import STATUS_CODES
from nougat.exceptions import *
from nougat.utils import is_middleware, empty
from nougat.config import Config
from nougat.logger import get_logger
from nougat.context import Request, Response

from typing import List, Callable, Dict
import asyncio


__all__ = ['Nougat']


class Nougat(object):

    # __slots__ = ['name', 'config', 'middleware', 'debug', 'start_server']

    def __init__(self, name: str ='Nougat APP') -> None:

        self.name: str = name

        self.config: 'Config' = Config()
        self.middleware: List[Callable] = []

        self.debug: bool = False

        self.port: int = None
        self.log = get_logger()

    def use(self, middleware: Callable):
        """
        Register Middleware
        :param middleware: The Middleware Function
        """

        if is_middleware(middleware):
            self.middleware.append(middleware)

    async def handler(self, request: Dict):
        """
        The handler handling each request
        :param request: the Request instance
        :return: The Response instance
        """
        request = Request.create_from_dict(self, request)
        response: 'Response' = Response()

        handler: Callable = empty
        chain_reverse = self.middleware[::-1]
        for middleware in chain_reverse:
                handler = partial(middleware, req=request, res=response, next=handler)

        try:

            await handler()

        except HttpException as e:
            response.status = e.status
            response.content = e.body

        response.output_generator()

        return response.status, STATUS_CODES.get(response.status, ''), response.header_as_list, response.output

    def run(self, host: str="localhost", port: int=8000, debug: bool=False):
        """
        start the http server
        :param host: The listening host
        :param port: The listening port
        :param debug: whether it is in debug mod or not
        """
        if debug:
            print("Nougat is listening on http://{}:{}\n".format(host, port))
        self.debug = debug
        loop = asyncio.get_event_loop()

        try:
            loop.run_until_complete(self.start_server(host, port))
            loop.run_forever()
        except KeyboardInterrupt:
            loop.close()

    async def start_server(self, host: str, port: int=8000):

        self.port = port
        return await serve(self.handler, None, host, port)
