import aiohttp
import asyncio
from functools import partial
from .protocol import HttpProtocol
from .middleware import BaseMiddleware

try:
    import uvloop
except:
    uvloop = asyncio


__all__ = ['TestClient']


HOST = '127.0.0.1'
PORT = 40401


class Proxy:
    pass

class TestClient(BaseMiddleware):
    app = None
    loop = None
    server = None
    response = None
    request = Proxy()

    def on_request(self, request):
        self.request.content = request

    def __init__(self, app=None):
        self.app = app
        self.loop = uvloop.new_event_loop()
        self.server = None
        self.response = None

    async def __local_request(self, method, url, *args, **kwargs):

        url = 'http://{host}:{port}{uri}'.format(host=HOST, port=PORT, uri=url)
        async with aiohttp.ClientSession() as session:
            async with getattr(session, method)(url, *args, **kwargs) as response:
                response.text = await response.text()
                self.response = response
                self.server.close()
                asyncio.get_event_loop().stop()

    def __request(self, method, url, *args, **kwargs):
        self.app.register_middleware(TestClient)

        asyncio.set_event_loop(self.loop)
        server_coroutine = self.loop.create_server(partial(HttpProtocol, loop=self.loop, app=self.app),
                                                   HOST, PORT)

        self.server = self.loop.run_until_complete(server_coroutine)

        self.loop.run_until_complete(self.__local_request(method, url, *args, **kwargs))

        return self.request.content, self.response

    def head(self, url, *args, **kwargs):
        return self.__request('head', url, *args, **kwargs)

    def get(self, url, *args, **kwargs):
        return self.__request('get', url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        return self.__request('post', url, *args, **kwargs)

    def put(self, url, *args, **kwargs):
        return self.__request('put', url, *args, **kwargs)

    def delete(self, url, *args, **kwargs):
        return self.__request('delete', url, *args, **kwargs)

    def options(self, url, *args, **kwargs):
        return self.__request('options', url, *args, **kwargs)

    def patch(self, url, *args, **kwargs):
        return self.__request('patch', url, *args, **kwargs)