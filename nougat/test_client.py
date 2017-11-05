from yarl import URL
import requests
import curio
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
        self.server = None

    async def real_request(self):
        print("doing it")
        return requests.get("http://localhost:40404/")

    async def async_request(self, proxy):
        async with curio.timeout_after(10):
            server = await curio.spawn(self.app.start_server, HOST, PORT)
            await curio.sleep(1)
            proxy.ret = await self.real_request()
            print("done")
        await server.cancel()

    def __request(self, method, url, *args, **kwargs):
        p = Proxy()
        curio.run(self.async_request, p)

        return p.ret

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
