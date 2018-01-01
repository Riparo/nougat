from nougat.router import Routing, ResourceRouting, get, post
from nougat import TestClient


class TestRouting:

    def test_redirect(self, app, router):

        class MainRouting(Routing):

            @get('/')
            async def index(self):

                self.redirect('/after')

            @get('/after')
            async def redirect_after(self):

                return 'redirect after'

        router.add(MainRouting)
        app.use(router)

        test = TestClient(app)
        res = test.get('/', allow_redirects=True)
        #
        assert res.url == test.url('/after')
        assert res.text == 'redirect after'

    def test_abort(self, app, router):

        class MainRouting(Routing):

            @get('/')
            async def index(self):
                self.abort(451, 'Legal Reasons')

        router.add(MainRouting)
        app.use(router)

        res = TestClient(app).get('/')
        assert res.status == 451
        assert res.text == 'Legal Reasons'


class TestAddCustomResponse:

    def test_add_header(self, app, router):

        class MainRouting(Routing):

            @get('/')
            async def index(self):
                self.response.set_header('Keyword', 'Value')

        router.add(MainRouting)
        app.use(router)

        res = TestClient(app).get('/')
        assert res.headers.get('Keyword', None) == 'Value'

    def test_add_cookies(self, app, router):

        class MainRouting(Routing):
            @get('/')
            async def index(self):
                self.response.set_cookies('Coo', 'Content')

        router.add(MainRouting)
        app.use(router)

        res = TestClient(app).get('/')
        assert res.cookies.get('Coo', None).value == 'Content'

    def test_custom_http_code(self, app, router):

        class MainRouting(Routing):

            @get('/')
            async def index(self):
                self.response.status = 400

        router.add(MainRouting)
        app.use(router)

        res = TestClient(app).get('/')
        assert res.status == 400

    def test_custom_response_type(self, app, router):

        class MainRouting(Routing):
            @get('/')
            async def index(self):
                self.response.type = 'application/json'
                return "[]"

        router.add(MainRouting)
        app.use(router)

        res = TestClient(app).get('/')
        assert res.content_type == 'application/json'
        assert res.text == '[]'

    def test_set_advanced_cookie(self, app, router):
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

        res = TestClient(app).get('/')
        assert res.cookies.get('Coo', None).value == 'Content'


class TestGetRoutingInformation:

    def test_get_from_query(self, app, router):

        class MainRouting(Routing):
            @get('/')
            async def index(self):
                return self.request.query.get('hello', None)

        router.add(MainRouting)
        app.use(router)

        res = TestClient(app).get('/')
        assert res.text == ''

        res = TestClient(app).get('/?hello=world')
        assert res.text == 'world'

    def test_get_from_form(self, app, router):

        class MainRouting(Routing):
            @post('/')
            async def index(self):
                hello = self.request.form.get('hello', None)
                if hello:
                    return hello[0]

        router.add(MainRouting)
        app.use(router)

        res = TestClient(app).post('/')
        assert res.text == ''

        res = TestClient(app).post('/', data={'hello': 'world'})
        assert res.text == 'world'

    def test_get_from_header(self, app, router):

        class MainRouting(Routing):

            @get('/')
            async def index(self):
                return self.request.headers.get('custom-header', 'None')

        router.add(MainRouting)
        app.use(router)

        res = TestClient(app).get('/', headers={'custom-header': 'hello world'})

        assert res.text == 'hello world'

    def test_get_from_cookie(self, app, router):

        class MainRouting(Routing):
            @get('/')
            async def index(self):
                return self.request.cookies.get('custom-cookie', 'hello world')

        router.add(MainRouting)
        app.use(router)

        res = TestClient(app).get('/', cookies={'custom-cookie': 'hello world', 'append': 'more'})

        assert res.text == '"hello world"'

    def test_get_ip(self, app, router):

        class MainRouting(Routing):
            @get('/')
            async def index(self):
                return self.request.ip

        router.add(MainRouting)
        app.use(router)

        res = TestClient(app).get('/')
        assert res.text == '127.0.0.1'

    def test_json(self, app, router):

        class MainRouting(Routing):
            @post('/')
            async def index(self):
                print(self.request.form)
                hello = self.request.form.get('hello', None)
                if hello:
                    return hello

        router.add(MainRouting)
        app.use(router)

        res = TestClient(app).post('/')
        assert res.text == ''

        res = TestClient(app).post('/', json={'hello': 'world'})
        assert res.text == 'world'
