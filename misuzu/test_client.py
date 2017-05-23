import aiohttp
import asyncio
from functools import partial
from yarl import URL
from misuzu.protocol import HttpProtocol
try:
    import uvloop
except:
    uvloop = asyncio


__all__ = ['TestClient']


HOST = '127.0.0.1'
PORT = 40404


class Proxy:
    ret = None


class TestClient:
    app = None
    loop = None
    server = None

    def __init__(self, app=None):
        self.app = app
        self.loop = uvloop.new_event_loop()
        self.server = None

    def __request(self, method, url, *args, **kwargs):

        ret = Proxy()

        async def test_middleware(ctx, next):
            await next()
            ctx.app.ctx = ctx

        def response_builder(_ret):
            def _response(future):
                _ret.ret = future.result()
                asyncio.get_event_loop().stop()
            return _response

        response_function = response_builder(ret)

        async def __local_request(method, url, future, *args, **kwargs):
            url = 'http://{host}:{port}{uri}'.format(host=HOST, port=PORT, uri=url)
            async with aiohttp.ClientSession(loop=self.loop) as session:
                async with getattr(session, method)(url, *args, **kwargs) as response:
                    response.text = await response.text()
                    future.set_result(response)
                    asyncio.get_event_loop().stop()

        self.app.chain.append(test_middleware)
        asyncio.set_event_loop(self.loop)

        server_coroutine = self.loop.create_server(partial(HttpProtocol, loop=self.loop, app=self.app), HOST, PORT)
        server_loop = self.loop.run_until_complete(server_coroutine)

        # set request
        request_future = asyncio.Future()
        asyncio.ensure_future(__local_request(method, url, request_future, *args, **kwargs), loop=self.loop)
        request_future.add_done_callback(response_function)
        self.loop.run_until_complete(request_future)

        self.loop.run_forever()

        server_loop.close()
        if not hasattr(self.app, "ctx"):
            self.app.ctx = None

        return ret.ret, self.app.ctx

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

    def url(self, path=""):
        """
        generate the abstract url for test case
        """

        return URL('http://{}:{}{}'.format(HOST, PORT, path))
