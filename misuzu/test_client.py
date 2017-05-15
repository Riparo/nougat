import aiohttp
import asyncio
from functools import partial
from misuzu.protocol import HttpProtocol
try:
    import uvloop
except:
    uvloop = asyncio


__all__ = ['TestClient']


HOST = '127.0.0.1'
PORT = 8000


class TestClient:
    app = None
    loop = None
    server = None

    def __init__(self, app=None):
        self.app = app
        self.loop = uvloop.new_event_loop()
        self.server = None

    def __request(self, method, url, *args, **kwargs):

        async def test_middleware(context, next):
            await next()
            context.app.ctx = context

        async def __local_request(method, url, *args, **kwargs):
            url = 'http://{host}:{port}{uri}'.format(host=HOST, port=PORT, uri=url)
            async with aiohttp.ClientSession(loop=self.loop) as session:
                async with getattr(session, method)(url, *args, **kwargs) as response:
                    asyncio.get_event_loop().stop()

        self.app.chain.append(test_middleware)
        asyncio.set_event_loop(self.loop)

        server_coroutine = self.loop.create_server(partial(HttpProtocol, loop=self.loop, app=self.app), HOST, PORT)
        server_loop = self.loop.run_until_complete(server_coroutine)
        self.loop.run_until_complete(__local_request(method, url, *args, **kwargs))
        self.loop.run_forever()
        return self.app.ctx.res, self.app.ctx

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
