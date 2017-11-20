import aiohttp
from yarl import URL
import asyncio

__all__ = ['TestClient']


HOST = '127.0.0.1'
PORT = 0


class Proxy:
    ret = None


class TestClient:
    app = None
    loop = None
    server = None

    def __init__(self, app=None):
        self.app = app
        self.loop = asyncio.new_event_loop()
        self.server = None
        self.port = None

    async def stop_server(self):
        loop = asyncio.get_event_loop()
        loop.stop()

    def __request(self, method, url, cookies=None, *args, **kwargs):

        async def __local_request(app, method, url, *args, **kwargs):

            server_loop = await app.start_server(HOST, PORT)
            self.port = server_loop.sockets[0].getsockname()[1]
            url = 'http://{host}:{port}{uri}'.format(host=HOST, port=self.port, uri=url)

            async with aiohttp.ClientSession(loop=self.loop, cookies=cookies) as session:
                async with getattr(session, method)(url, *args, **kwargs) as response:
                    response.text = await response.text()
                    server_loop.close()
                    await server_loop.wait_closed()
                    return response

        asyncio.set_event_loop(self.loop)
        ret = self.loop.run_until_complete(__local_request(self.app, method, url, *args, **kwargs))

        # cancel all task
        tasks = asyncio.Task.all_tasks()
        for task in tasks:
            task.cancel()
        self.loop.run_until_complete(self.stop_server())

        return ret

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

        return URL('http://{}:{}{}'.format(HOST, self.port, path))
