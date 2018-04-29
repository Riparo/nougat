import aiohttp
from yarl import URL

__all__ = ['TestClient']


class TestClient:

    def __init__(self, app, port: int):
        self.app = app
        self.port = port

    async def __aenter__(self):

        await self.app.start_server('127.0.0.1', self.port)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.app.server.close()
        await self.app.server.wait_closed()

    async def __request(self, method, url, cookies=None, *args, **kwargs):

        url = 'http://127.0.0.1:{port}{uri}'.format(port=self.port, uri=url)

        async with aiohttp.ClientSession(cookies=cookies) as session:
            async with getattr(session, method)(url, *args, **kwargs) as response:
                content = await response.text()
                response.text = content

        return response

    async def head(self, url, *args, **kwargs):
        return await self.__request('head', url, *args, **kwargs)

    async def get(self, url, *args, **kwargs):
        return await self.__request('get', url, *args, **kwargs)

    async def post(self, url, *args, **kwargs):
        return await self.__request('post', url, *args, **kwargs)

    async def put(self, url, *args, **kwargs):
        return await self.__request('put', url, *args, **kwargs)

    async def delete(self, url, *args, **kwargs):
        return await self.__request('delete', url, *args, **kwargs)

    async def options(self, url, *args, **kwargs):
        return await self.__request('options', url, *args, **kwargs)

    async def patch(self, url, *args, **kwargs):
        return await self.__request('patch', url, *args, **kwargs)

    def url(self, path: str="/"):
        return URL('http://{}:{}{}'.format('127.0.0.1', self.port, path))
