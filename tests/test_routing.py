from nougat import Nougat, get, Routing, TestClient, post


class TestRouting:

    def test_redirect(self, app):

        class MainRouting(Routing):

            @get('/')
            async def index(self):

                self.redirect('/after')

            @get('/after')
            async def redirect_after(self):

                return 'redirect after'

        app.route(MainRouting)

        test = TestClient(app)
        res = test.get('/', allow_redirects=True)
        #
        assert res.url == test.url('/after')
        assert res.text == 'redirect after'

    def test_abort(self, app):

        class MainRouting(Routing):

            @get('/')
            async def index(self):
                self.abort(451, 'Legal Reasons')

        app.route(MainRouting)

        res = TestClient(app).get('/')
        assert res.status == 451
        assert res.text == 'Legal Reasons'


class TestAddCustomResponse:

    def test_add_header(self, app):

        class MainRouting(Routing):

            @get('/')
            async def index(self):
                self.response.set_header('Keyword', 'Value')

        app.route(MainRouting)

        res = TestClient(app).get('/')
        assert res.headers.get('Keyword', None) == 'Value'

    def test_add_cookies(self, app):

        class MainRouting(Routing):
            @get('/')
            async def index(self):
                self.response.set_cookies('Coo', 'Content')

        app.route(MainRouting)

        res = TestClient(app).get('/')
        assert res.cookies.get('Coo', None).value == 'Content'

    def test_custom_http_code(self, app):

        class MainRouting(Routing):

            @get('/')
            async def index(self):
                self.response.status = 400

        app.route(MainRouting)

        res = TestClient(app).get('/')
        assert res.status == 400

    def test_custom_response_type(self, app):

        class MainRouting(Routing):
            @get('/')
            async def index(self):
                self.response.type = 'application/json'
                return "[]"

        app.route(MainRouting)

        res = TestClient(app).get('/')
        assert res.content_type == 'application/json'
        assert res.text == '[]'


class TestGetRoutingInformation:

    def test_get_from_query(self, app):

        class MainRouting(Routing):
            @get('/')
            async def index(self):
                return self.request.query.get('hello', None)

        app.route(MainRouting)

        res = TestClient(app).get('/')
        assert res.text == 'OK'

        res = TestClient(app).get('/?hello=world')
        assert res.text == 'world'

    def test_get_from_form(self, app):

        class MainRouting(Routing):
            @post('/')
            async def index(self):
                hello = self.request.form.get('hello', None)
                if hello:
                    return hello[0]

        app.route(MainRouting)

        res = TestClient(app).post('/')
        assert res.text == 'OK'

        res = TestClient(app).post('/', data={'hello': 'world'})
        assert res.text == 'world'

    def test_get_from_header(self, app):

        class MainRouting(Routing):

            @get('/')
            async def index(self):
                return self.request.headers.get('custom-header', 'None')

        app.route(MainRouting)

        res = TestClient(app).get('/', headers={'custom-header': 'hello world'})

        assert res.text == 'hello world'

    def test_get_from_cookie(self, app):

        class MainRouting(Routing):
            @get('/')
            async def index(self):
                return self.request.cookies.get('custom-cookie', 'hello world')

        app.route(MainRouting)

        res = TestClient(app).get('/', cookies={'custom-cookie': 'hello world', 'append': 'more'})

        assert res.text == '"hello world"'
