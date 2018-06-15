
from typing import Callable, List, Awaitable, Tuple
import asyncio
from nougat.signal import Signal
from nougat.asgi import serve
from nougat.manage import Manager
from nougat.config import Config
from nougat.utils import is_middleware, empty, map_context_to_middleware
from nougat.context import Request, Response
from nougat.exceptions import HttpException


MiddlewareType = Callable[..., Awaitable[None]]

ALLOWED_SIGNALS = ['before_start', 'after_start']


class Nougat:

    def __init__(self, name: str ='Nougat') -> None:

        self.app = name
        self.server = None

        self.config = Config()

        self.middleware: List[MiddlewareType] = []

        self.signal_manager = Signal(self)
        self.signal = self.signal_manager.listen
        self.manager = Manager(self)

        self.debug: bool = False

    def use(self, *middleware: MiddlewareType) -> None:
        """
        Register Middleware
        :param middleware: The Middleware Function
        """
        for m in middleware:
            if is_middleware(m):
                self.middleware.append(m)

    async def handler(self, request: Request) -> Tuple[int, str, List[Tuple[str, str]], bytes]:
        """
        The handler handling each request
        :param request: the Request instance
        :return: The Response instance
        """
        response: 'Response' = Response()

        handler: Callable = empty
        chain_reverse = self.middleware[::-1]
        for middleware in chain_reverse:
            handler = map_context_to_middleware(middleware, self, request, response, handler)

        try:
            await handler()

        except HttpException as e:
            response.code = e.code
            response.content = e.body

        return response.code, response.status, response.header_as_list, response.output

    def run(self, host: str="localhost", port: int=8000, debug: bool=False):
        """
        start the http server
        :param host: The listening host
        :param port: The listening port
        :param debug: whether it is in debug mod or not
        """
        self.debug = debug
        loop = asyncio.get_event_loop()

        try:
            loop.run_until_complete(self.start_server(host, port))
            loop.run_forever()
        except KeyboardInterrupt:
            loop.run_until_complete(self.signal_manager.activate('before_close'))
            loop.run_until_complete(self.close_server_async())
            loop.run_until_complete(self.signal_manager.activate('after_close'))
            loop.run_until_complete(asyncio.gather(*asyncio.Task.all_tasks()))
            loop.close()

    async def close_server_async(self):
        self.server.close()
        await self.server.wait_closed()

    async def start_server(self, host: str, port: int=8000):

        # active before_start signal
        await self.signal_manager.activate('before_start')

        self.server = await serve(self.handler, None, host, port)

        # active after_start signal
        await self.signal_manager.activate('after_start')
