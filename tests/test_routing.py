from nougat.router import Routing, ResourceRouting, get, post
from nougat import TestClient
import pytest


class TestRouting:

    @pytest.mark.asyncio
    async def test_redirect(self, app, router, port):

        class MainRouting(Routing):

            @get('/')
            async def index(self):

                self.redirect('/after')

            @get('/after')
            async def redirect_after(self):

                return 'redirect after'

        router.add(MainRouting)
        app.use(router)

        async with TestClient(app, port) as client:

            test = await client.get('/')
            assert test.url == client.url('/after')
            assert test.text == 'redirect after'

    @pytest.mark.asyncio
    async def test_abort(self, app, router, port):

        class MainRouting(Routing):

            @get('/')
            async def index(self):
                self.abort(451, 'Legal Reasons')

        router.add(MainRouting)
        app.use(router)

        async with TestClient(app, port) as client:
            res = await client.get('/')
            assert res.status == 451
            assert res.text == 'Legal Reasons'


class TestAddCustomResponse:

    @pytest.mark.asyncio
    async def test_add_header(self, app, router, port):

        class MainRouting(Routing):

            @get('/')
            async def index(self):
                self.response.set_header('Keyword', 'Value')

        router.add(MainRouting)
        app.use(router)

        async with TestClient(app, port) as client:
            res = await client.get('/')
            assert res.headers.get('Keyword', None) == 'Value'

    @pytest.mark.asyncio
    async def test_add_cookies(self, app, router, port):

        class MainRouting(Routing):
            @get('/')
            async def index(self):
                self.response.set_cookies('Coo', 'Content')

        router.add(MainRouting)
        app.use(router)

        async with TestClient(app, port) as client:
            res = await client.get('/')
            assert res.cookies.get('Coo', None).value == 'Content'

    @pytest.mark.asyncio
    async def test_custom_http_code(self, app, router, port):

        class MainRouting(Routing):

            @get('/')
            async def index(self):
                self.response.status = 400

        router.add(MainRouting)
        app.use(router)

        async with TestClient(app, port) as client:
            res = await client.get('/')
            assert res.status == 400

    @pytest.mark.asyncio
    async def test_custom_response_type(self, app, router, port):

        class MainRouting(Routing):
            @get('/')
            async def index(self):
                self.response.type = 'application/json'
                return "[]"

        router.add(MainRouting)
        app.use(router)

        async with TestClient(app, port) as client:
            res = await client.get('/')
            assert res.content_type == 'application/json'
            assert res.text == '[]'

    @pytest.mark.asyncio
    async def test_set_advanced_cookie(self, app, router, port):
        class MainRouting(Routing):
            @get('/')
            async def index(self):
                self.response.set_cookies(
                    'Coo', 'Content',
                    expires=10,
                    domain='127.0.0.1',
                    path='/',
                    secure=True,
                    http_only=True,
                    same_site='127.0.0.1:8000'
                )

        router.add(MainRouting)
        app.use(router)

        async with TestClient(app, port) as client:
            res = await client.get('/')
            assert res.cookies.get('Coo', None).value == 'Content'


class TestGetRoutingInformation:

    @pytest.mark.asyncio
    async def test_get_from_query(self, app, router, port):

        class MainRouting(Routing):
            @get('/')
            async def index(self):
                return self.request.query.get('hello', None)

        router.add(MainRouting)
        app.use(router)

        async with TestClient(app, port) as client:
            res = await client.get('/')
            assert res.text == ''

            res = await client.get('/?hello=world')
            assert res.text == 'world'

    @pytest.mark.asyncio
    async def test_get_from_form(self, app, router, port):

        class MainRouting(Routing):
            @post('/')
            async def index(self):
                hello = self.request.form.get('hello', None)
                if hello:
                    return hello[0]

        router.add(MainRouting)
        app.use(router)

        async with TestClient(app, port) as client:
            res = await client.post('/')
            assert res.text == ''

            res = await client.post('/', data={'hello': 'world'})
            assert res.text == 'world'

    @pytest.mark.asyncio
    async def test_get_from_header(self, app, router, port):

        class MainRouting(Routing):

            @get('/')
            async def index(self):
                return self.request.headers.get('custom-header', 'None')

        router.add(MainRouting)
        app.use(router)

        async with TestClient(app, port) as client:
            res = await client.get('/', headers={'custom-header': 'hello world'})

            assert res.text == 'hello world'

    @pytest.mark.asyncio
    async def test_get_from_cookie(self, app, router, port):

        class MainRouting(Routing):
            @get('/')
            async def index(self):
                return self.request.cookies.get('custom-cookie', 'hello world')

        router.add(MainRouting)
        app.use(router)

        async with TestClient(app, port) as client:
            res = await client.get('/', cookies={'custom-cookie': 'hello world', 'append': 'more'})

            assert res.text == '"hello world"'

    @pytest.mark.asyncio
    async def test_get_ip(self, app, router, port):

        class MainRouting(Routing):
            @get('/')
            async def index(self):
                return self.request.ip

        router.add(MainRouting)
        app.use(router)

        async with TestClient(app, port) as client:
            res = await client.get('/')
            assert res.text == '127.0.0.1'

    @pytest.mark.asyncio
    async def test_json(self, app, router, port):

        class MainRouting(Routing):
            @post('/')
            async def index(self):
                hello = self.request.form.get('hello', None)
                if hello:
                    return hello

        router.add(MainRouting)
        app.use(router)

        async with TestClient(app, port) as client:
            res = await client.post('/')
            assert res.text == ''

            res = await client.post('/', json={'hello': 'world'})
            assert res.text == 'world'
