import logging
from functools import partial
from nougat.exceptions import *
from nougat.utils import is_middleware, empty
from nougat.config import Config

from nougat.context import Request, Response

from nougat.http_wrapper import HTTPWrapper
from typing import List, Callable
import asyncio


__all__ = ['Nougat']


class Nougat(object):

    __slots__ = ['name', 'config', '__chain', 'debug']

    def __init__(self, name: str ='Nougat APP') -> None:

        self.name: str = name

        self.config: 'Config' = Config()
        self.__chain: List[Callable] = []

        self.debug: bool = False

    def use(self, middleware: Callable):
        """
        Register Middleware
        :param middleware: The Middleware Function
        """

        if is_middleware(middleware):
            self.__chain.append(middleware)

    async def handler(self, request: 'Request'):
        """
        The handler handling each request
        :param request: the Request instance
        :return: The Response instance
        """

        response: 'Response' = Response()

        handler: Callable = empty
        chain_reverse = self.__chain[::-1]
        for middleware in chain_reverse:
                handler = partial(middleware, req=request, res=response, next=handler)

        try:

            await handler()

        except HttpException as e:
            response.status = e.status
            response.content = e.body

        return response

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
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.start_server(host, port))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            loop.close()

    async def start_server(self, host: str, port: int):

        return await asyncio.start_server(self.http_serve, host, port)

    async def http_serve(self, reader, writer):
        """
        the income function of curio.tcp_server
        """
        address = writer.get_extra_info('peername')
        await HTTPWrapper((reader, writer), address).process(self)
