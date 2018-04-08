from nougat import *
from nougat.router import *
from nougat.test_client import TestClient
from aiohttp import FormData
import pytest


class TestBasicApplication:

    @pytest.mark.asyncio
    async def test_get(self, app, router, port):

        class Basic(Routing):

            @get('/')
            async def index(self):
                return 'hello world'

        router.add(Basic)
        app.use(router)
        async with TestClient(app, port) as client:
            res = await client.get('/')
            assert res.text == 'hello world'

    @pytest.mark.asyncio
    async def test_post(self, app, router, port):

        class Basic(Routing):
            @post('/')
            async def index(self):
                return 'post method'

        router.add(Basic)
        app.use(router)
        async with TestClient(app, port) as client:
            res = await client.post('/')
            assert res.text == 'post method'

    @pytest.mark.asyncio
    async def test_put(self, app, router, port):

        class Basic(Routing):
            @put('/')
            async def index(self):
                return 'put method'

        router.add(Basic)
        app.use(router)

        async with TestClient(app, port) as client:
            res = await client.put('/')
            assert res.text == 'put method'

    @pytest.mark.asyncio
    async def test_patch(self, app, router, port):

        class Basic(Routing):
            @patch('/')
            async def index(self):
                return 'patch method'

        router.add(Basic)
        app.use(router)

        async with TestClient(app, port) as client:
            res = await client.patch('/')
            assert res.text == 'patch method'

    @pytest.mark.asyncio
    async def test_delete(self, app, router, port):

        class Basic(Routing):
            @delete('/')
            async def index(self):
                return 'delete method'

        router.add(Basic)
        app.use(router)

        async with TestClient(app, port) as client:
            res = await client.delete('/')
            assert res.text == 'delete method'


class TestRouter:

    @pytest.mark.asyncio
    async def test_static(self, app, router, port):

        class MainRouting(Routing):

            @get('/static')
            async def static_route(self):
                return 'static route'

        router.add(MainRouting)
        app.use(router)

        async with TestClient(app, port) as client:
            res = await client.get('/static')
            assert res.text == 'static route'

            res = await client.get('/')
            assert res.status == 404

    @pytest.mark.asyncio
    async def test_simple_type(self, app, router, port):

        class MainRouting(Routing):

            @get('/article/:id')
            async def article_simple(self):
                return 'id: {}'.format(self.request.url_dict.get('id'))

        router.add(MainRouting)
        app.use(router)

        async with TestClient(app, port) as client:
            res = await client.get('/article/')
            assert res.status == 404
            assert res.text == ''

            res = await client.get('/article/123')
            assert res.text == 'id: 123'

            res = await client.get('/article/word')
            assert res.text == 'id: word'

            res = await client.get('/article/path/123')
            assert res.text == ''

    @pytest.mark.asyncio
    async def test_unnamed_regex(self, app, router, port):

        class MainRouting(Routing):
            @get('/article/[0-9]+')
            async def article_simple(self):
                return 'hit'

        router.add(MainRouting)
        app.use(router)

        async with TestClient(app, port) as client:
            res = await client.get('/article/')
            assert res.text == ''

            res = await client.get('/article/123')
            assert res.text == 'hit'

            res = await client.get('/article/word')
            assert res.text == ''

            res = await client.get('/article/path/123')
            assert res.text == ''

    @pytest.mark.asyncio
    async def test_named_regex(self, app, router, port):

        class MainRouting(Routing):
            @get('/article/:id<[0-9]+>')
            async def article_simple(self):
                return self.request.url_dict.get('id', 'None')

        router.add(MainRouting)
        app.use(router)

        async with TestClient(app, port) as client:
            res = await client.get('/article/')
            assert res.text == ''

            res = await client.get('/article/123')
            assert res.text == '123'

            res = await client.get('/article/word')
            assert res.text == ''

            res = await client.get('/article/path/123')
            assert res.text == ''

    @pytest.mark.asyncio
    async def tes_form_data_with_multipart(self, app, router, port):
        class MainRouting(Routing):

            @post('/')
            async def multipart(self):
                name = self.request.form.get('file')
                return name.name

        router.add(MainRouting)
        app.use(router)

        data = FormData()
        data.add_field('name', 'foo')
        data.add_field('file', 'file content',
                       filename='file.file',
                       content_type='image/img')

        async with TestClient(app, port) as client:
            res = await client.post('/', data=data)
            assert res.text == 'file.file'

class TestMiddleware:

    @pytest.mark.asyncio
    async def test_basic(self, app, router, port):

        async def middleware(req, res, next):

            await next()
            res.content = 'hello'

        app.use(middleware)

        class MainRouting(Routing):

            @get('/')
            async def index(self):
                return 'hello world'

        router.add(MainRouting)
        app.use(router)

        async with TestClient(app, port) as client:
            res = await client.get('/')

            assert res.text == 'hello'
