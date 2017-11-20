from nougat import Nougat
from nougat.routing import Routing, get, post, put, patch ,delete
from nougat.test_client import TestClient
from aiohttp import FormData


class TestBasicApplication:

    def test_get(self, app):

        class Basic(Routing):

            @get('/')
            async def index(self):
                return 'hello world'

        app.route(Basic)

        res = TestClient(app).get('/')
        assert res.text == 'hello world'

    def test_post(self, app):

        class Basic(Routing):
            @post('/')
            async def index(self):
                return 'post method'

        app.route(Basic)

        res = TestClient(app).post('/')
        assert res.text == 'post method'

    def test_put(self, app):

        class Basic(Routing):
            @put('/')
            async def index(self):
                return 'put method'

        app.route(Basic)

        res = TestClient(app).put('/')
        assert res.text == 'put method'

    def test_patch(self, app):

        class Basic(Routing):
            @patch('/')
            async def index(self):
                return 'patch method'

        app.route(Basic)

        res = TestClient(app).patch('/')
        assert res.text == 'patch method'

    def test_delete(self, app):

        class Basic(Routing):
            @delete('/')
            async def index(self):
                return 'delete method'

        app.route(Basic)

        res = TestClient(app).delete('/')
        assert res.text == 'delete method'


class TestRouter:

    def test_static(self, app):

        class MainRouting(Routing):

            @get('/static')
            async def static_route(self):
                return 'static route'

        app.route(MainRouting)

        res = TestClient(app).get('/static')
        assert res.text == 'static route'

        res = TestClient(app).get('/')
        assert res.text == 'Not Found'

    def test_simple_type(self, app):

        class MainRouting(Routing):

            @get('/article/:id')
            async def article_simple(self):
                return 'id: {}'.format(self.request.url_dict.get('id'))

        app.route(MainRouting)

        res = TestClient(app).get('/article/')
        assert res.text == 'Not Found'

        res = TestClient(app).get('/article/123')
        assert res.text == 'id: 123'

        res = TestClient(app).get('/article/word')
        assert res.text == 'id: word'

        res = TestClient(app).get('/article/path/123')
        assert res.text == 'Not Found'

    def test_unnamed_regex(self, app):

        class MainRouting(Routing):
            @get('/article/[0-9]+')
            async def article_simple(self):
                return 'hit'

        app.route(MainRouting)

        res = TestClient(app).get('/article/')
        assert res.text == 'Not Found'

        res = TestClient(app).get('/article/123')
        assert res.text == 'hit'

        res = TestClient(app).get('/article/word')
        assert res.text == 'Not Found'

        res = TestClient(app).get('/article/path/123')
        assert res.text == 'Not Found'

    def test_named_regex(self, app):

        class MainRouting(Routing):
            @get('/article/:id<[0-9]+>')
            async def article_simple(self):
                return self.request.url_dict.get('id', 'None')

        app.route(MainRouting)

        res = TestClient(app).get('/article/')
        assert res.text == 'Not Found'

        res = TestClient(app).get('/article/123')
        assert res.text == '123'

        res = TestClient(app).get('/article/word')
        assert res.text == 'Not Found'

        res = TestClient(app).get('/article/path/123')
        assert res.text == 'Not Found'

    def test_form_data_with_multipart(self, app):

        class MainRouting(Routing):

            @post('/')
            async def multipart(self):
                name = self.request.form.get('file')
                return name.name

        app.route(MainRouting)

        data = FormData()
        data.add_field('name', 'foo')
        data.add_field('file', 'file content',
                       filename='avatar.webp',
                       content_type='image/webp')

        res = TestClient(app).post('/', data=data)
        assert res.text == 'avatar.webp'


class TestMiddleware:

    def test_basic(self, app):

        async def middleware(context, next):

            await next()
            context.response.res = 'hello'

        app.use(middleware)

        class MainRouting(Routing):

            @get('/')
            async def index(self):
                return 'hello world'

        app.route(MainRouting)

        res = TestClient(app).get('/')

        assert res.text == 'hello'
