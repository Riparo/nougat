import aiohttp
import asyncio
from functools import partial
from yarl import URL
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
    res = None

    def __init__(self, app):
        self.app = app
        self.loop = asyncio.new_event_loop()
        self.server = None

    def listen(self, loop):
        self.server = loop.create_server(partial(HttpProtocol, loop=self.loop, app=self.app), HOST)
        print('hello')

    def __request_callback(self, future):
        self.res = future.result()
        print("123")
        asyncio.get_event_loop().stop()

    async def __local_request(self, future, method, url, cookies=None, *args, **kwargs):
        url = 'http://{host}:{port}{uri}'.format(host=HOST, port=PORT, uri=url)
        async with aiohttp.ClientSession(loop=self.loop, cookies=cookies) as session:
            async with getattr(session, method)(url, *args, **kwargs) as response:
                response.res_text = await response.text()
                future.set_result(response)

    def __request(self, method, url, *args, **kwargs):

        asyncio.set_event_loop(self.loop)

        server_coroutine = self.loop.create_server(partial(HttpProtocol, loop=self.loop, app=self.app), HOST, PORT)
        server_loop = self.loop.run_until_complete(server_coroutine)
        # set request
        request_future = asyncio.Future()
        asyncio.ensure_future(self.__local_request(request_future, method, url, *args, **kwargs), loop=self.loop)
        request_future.add_done_callback(self.__request_callback)
        #
        print("server loop start")

        print("request future start")
        # self.loop.run_until_complete(request_future)
        # self.loop.run_until_complete(asyncio.gather([server_coroutine, request_future]))
        self.loop.run_forever()
        print("123")
        server_loop.close()

        return self.res

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
