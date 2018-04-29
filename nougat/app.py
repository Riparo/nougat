
from typing import Callable, List, Dict, Awaitable, Tuple
import inspect
import asyncio
from nougat.asgi import serve
from nougat.config import Config
from nougat.utils import is_middleware, empty, map_context_to_middleware
from nougat.context import Request, Response
from nougat.exceptions import HttpException, UnknownSignalException


MiddlewareType = Callable[..., Awaitable[None]]
SignalType = Callable[['Nougat'], Awaitable[None]]


ALLOWED_SIGNALS = ['before_start', 'after_start']


class Nougat:

    def __init__(self, name: str ='Nougat') -> None:

        self.app = name
        self.server = None

        self.config = Config()

        self.middleware: List[MiddlewareType] = []
        self.signals: Dict[str, List[SignalType]] = {}

        self.debug: bool = False

        for signal in ALLOWED_SIGNALS:
            self.signals[signal] = []

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

    def signal(self, name: str):

        if name not in ALLOWED_SIGNALS:
            raise UnknownSignalException(name)

        def add_signal_handler(func: SignalType):
            self.signals[name].append(func)

        return add_signal_handler

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
            loop.close()

    async def start_server(self, host: str, port: int=8000):

        # active before_start signal

        for signal_func in self.signals['before_start']:
            if inspect.iscoroutinefunction(signal_func):
                await signal_func(self)
            else:
                signal_func(self)

        self.server = await serve(self.handler, None, host, port)

        # active after_start signal

        for signal_func in self.signals['after_start']:
            if inspect.iscoroutinefunction(signal_func):
                await signal_func(self)
            else:
                signal_func(self)
