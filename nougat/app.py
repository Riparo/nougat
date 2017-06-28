import asyncio
import logging
import signal
import sys
import inspect
from functools import partial
from nougat.router import Router, Param
from nougat.protocol import HttpProtocol
from nougat.test_client import TestClient
from nougat.section import Section
from nougat.exceptions import *
from nougat.utils import is_middleware
from nougat.config import Config

try:
    import uvloop
except:
    uvloop = asyncio

__all__ = ['Nougat']


class Nougat(object):

    def __init__(self, name='Nougat APP'):

        self.name = name
        self.__test_client = None
        self.router = Router(self.name)

        self.config = Config()
        self.chain = []

        self.sections = {}

    def use(self, middleware_or_section_name):
        """
        register middleware or section 
        """
        if isinstance(middleware_or_section_name, Section):
            # register section
            section = middleware_or_section_name
            if section.name in self.sections:
                raise NougatRuntimeError("it seems that this section's name had been used")
            logging.debug("register section {}".format(section.name))
            self.sections[section.name] = section

            self.router.union(section.router)
        elif inspect.isfunction(middleware_or_section_name):
            # register middleware
            is_middleware(middleware_or_section_name)
            middleware = middleware_or_section_name
            self.chain.insert(0, middleware)
        else:
            raise NougatRuntimeError("nougat only can use section instance or middleware function")

    async def handler(self, context, handler_future):

        try:
            # find route
            route = self.router.get(context)
            if not route:
                raise HttpException(None, 404)

            section = self.sections.get(route.section_name)
            context.generate_params(route)

            handler = partial(section.handler, context=context, route=route)

            for middleware in self.chain:
                handler = partial(middleware, ctx=context, next=handler)

            await handler()

        except HttpException as e:

            context.status = e.status
            context.res = e.body

        handler_future.set_result(context)

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

    def doc(self):
        """
        generate the api document
        :return: 
        """
        return {
            'name': self.name,
            'sections': [section.doc() for _, section in self.sections.items()]
        }