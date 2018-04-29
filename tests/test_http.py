import pytest
from aiohttp import FormData
from nougat import Nougat, TestClient
from nougat.context import Response, Request
from nougat.exceptions import HttpException


class TestHTTPFunctions:

    @pytest.mark.asyncio
    async def test_base_http_methods(self, app: Nougat, port: int):

        async def middleware(response: Response):

            response.code = 200
            response.content = 'Hello World'

        app.use(middleware)

        async with TestClient(app, port) as client:

            assert (await client.head('/')).text == ''
            assert (await client.options('/')).text == 'Hello World'
            assert (await client.get('/')).text == 'Hello World'
            assert (await client.post('/')).text == 'Hello World'
            assert (await client.put('/')).text == 'Hello World'
            assert (await client.patch('/')).text == 'Hello World'
            assert (await client.delete('/')).text == 'Hello World'

    @pytest.mark.asyncio
    async def test_raise_http_exception(self, app: Nougat, port: int):
        async def middleware(response: Response):

            raise HttpException(404, 'Not Found')

        app.use(middleware)

        async with TestClient(app, port) as client:

            res = await client.get('/')
            assert res.status == 404
            assert res.text == 'Not Found'


    @pytest.mark.asyncio
    async def test_custom_header(self, app: Nougat, port: int):
        async def middleware(response: Response):

            response.set_header('Hello', 'world')

        app.use(middleware)

        async with TestClient(app, port) as client:

            res = await client.get('/')
            assert res.headers['Hello'] == 'world'

    @pytest.mark.asyncio
    async def test_custom_cookies(self, app: Nougat, port: int):
        async def middleware(response: Response):

            response.set_cookies('time', 'now')

        app.use(middleware)

        async with TestClient(app, port) as client:

            res = await client.get('/')
            assert res.headers.get('Set-Cookie') == 'time=now'

    @pytest.mark.asyncio
    async def test_completed_cookies(self, app: Nougat, port: int):
        async def middleware(response: Response):
            response.set_cookies('time', 'now',
                                 expires=1,
                                 domain='127.0.0.1',
                                 path='/',
                                 secure=True,
                                 http_only=True,
                                 same_site='127.0.0.1')

        app.use(middleware)

        async with TestClient(app, port) as client:
            res = await client.get('/')
            wanted = res.headers.get('Set-Cookie')
            assert wanted == 'time=now; Max-Age=1; Domain=127.0.0.1; Path=/; Secure; HttpOnly; SameSite=127.0.0.1'

    @pytest.mark.asyncio
    async def test_send_data_through_json(self, app: Nougat, port: int):
        async def middleware(request: Request, response: Response):
            response.content = request.form.get('name')

        app.use(middleware)
        async with TestClient(app, port) as client:
            res = await client.post('/', json={'name': 'bar'})
            assert res.text == 'bar'

    @pytest.mark.asyncio
    async def test_send_data_through_x_form(self, app: Nougat, port: int):
        async def middleware(request: Request, response: Response):
            response.content = request.form.get('name')[0]

        app.use(middleware)
        async with TestClient(app, port) as client:
            res = await client.post('/', data={'name': 'bar'})
            assert res.text == 'bar'

    @pytest.mark.asyncio
    async def test_send_data_through_form_data(self, app: Nougat, port: int):
        async def middleware(request: Request, response: Response):
            response.content = request.form.get('file').name

        app.use(middleware)

        data = FormData()
        data.add_field('name', 'foo')
        data.add_field('file', 'file content',
                       filename='file.file',
                       content_type='image/img')

        async with TestClient(app, port) as client:
            res = await client.post('/', data=data)
            assert res.text == 'file.file'
