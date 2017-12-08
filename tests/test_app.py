from nougat.router import Routing, get, post, put, patch, delete
from nougat.test_client import TestClient
from aiohttp import FormData


class TestBasicApplication:

    def test_get(self, app, router):

        class Basic(Routing):

            @get('/')
            async def index(self):
                return 'hello world'

        router.add(Basic)
        app.use(router)

        res = TestClient(app).get('/')
        assert res.text == 'hello world'

    def test_post(self, app, router):

        class Basic(Routing):
            @post('/')
            async def index(self):
                return 'post method'

        router.add(Basic)
        app.use(router)

        res = TestClient(app).post('/')
        assert res.text == 'post method'

    def test_put(self, app, router):

        class Basic(Routing):
            @put('/')
            async def index(self):
                return 'put method'

        router.add(Basic)
        app.use(router)

        res = TestClient(app).put('/')
        assert res.text == 'put method'

    def test_patch(self, app, router):

        class Basic(Routing):
            @patch('/')
            async def index(self):
                return 'patch method'

        router.add(Basic)
        app.use(router)

        res = TestClient(app).patch('/')
        assert res.text == 'patch method'

    def test_delete(self, app, router):

        class Basic(Routing):
            @delete('/')
            async def index(self):
                return 'delete method'

        router.add(Basic)
        app.use(router)

        res = TestClient(app).delete('/')
        assert res.text == 'delete method'


class TestRouter:

    def test_static(self, app, router):

        class MainRouting(Routing):

            @get('/static')
            async def static_route(self):
                return 'static route'

        router.add(MainRouting)
        app.use(router)

        res = TestClient(app).get('/static')
        assert res.text == 'static route'

        res = TestClient(app).get('/')
        assert res.status == 404

    def test_simple_type(self, app, router):

        class MainRouting(Routing):

            @get('/article/:id')
            async def article_simple(self):
                return 'id: {}'.format(self.request.url_dict.get('id'))

        router.add(MainRouting)
        app.use(router)

        res = TestClient(app).get('/article/')
        assert res.status == 404
        assert res.text == ''

        res = TestClient(app).get('/article/123')
        assert res.text == 'id: 123'

        res = TestClient(app).get('/article/word')
        assert res.text == 'id: word'

        res = TestClient(app).get('/article/path/123')
        assert res.text == ''

    def test_unnamed_regex(self, app, router):

        class MainRouting(Routing):
            @get('/article/[0-9]+')
            async def article_simple(self):
                return 'hit'

        router.add(MainRouting)
        app.use(router)

        res = TestClient(app).get('/article/')
        assert res.text == ''

        res = TestClient(app).get('/article/123')
        assert res.text == 'hit'

        res = TestClient(app).get('/article/word')
        assert res.text == ''

        res = TestClient(app).get('/article/path/123')
        assert res.text == ''

    def test_named_regex(self, app, router):

        class MainRouting(Routing):
            @get('/article/:id<[0-9]+>')
            async def article_simple(self):
                return self.request.url_dict.get('id', 'None')

        router.add(MainRouting)
        app.use(router)

        res = TestClient(app).get('/article/')
        assert res.text == ''

        res = TestClient(app).get('/article/123')
        assert res.text == '123'

        res = TestClient(app).get('/article/word')
        assert res.text == ''

        res = TestClient(app).get('/article/path/123')
        assert res.text == ''

    def test_form_data_with_multipart(self, app, router):

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

        res = TestClient(app).post('/', data=data)
        assert res.text == 'file.file'


class TestMiddleware:

    def test_basic(self, app, router):

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

        res = TestClient(app).get('/')

        assert res.text == 'hello'
