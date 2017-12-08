import json
import pytest
from nougat import TestClient
from nougat.router import *
from nougat.exceptions import *


class TestRestfulExtension:

    def test_basis_parameter(self, app, router):

        class MainRouting(ResourceRouting):

            @get('/')
            @param('name', str)
            async def static_route(self):
                return 'hello {}'.format(self.params.name)

        router.add(MainRouting)
        app.use(router)

        res = TestClient(app).get('/?name=world')
        assert res.text == 'hello world'

        res = TestClient(app).get('/')
        assert res.text == json.dumps({'name': 'miss parameter'})

    def test_location(self, app, router):
        class MainRouting(ResourceRouting):

            @get('/url/:id')
            @param('id', int, location='url')
            async def url_param(self):
                return str(self.params.id)

            @get('/query')
            @param('name', str, location='query')
            async def query_param(self):
                return self.params.name

            @post('/post')
            @param('name', str, location='form')
            async def form_param(self):
                return self.params.name

            @get('/header')
            @param('name', str, location='header')
            async def header_param(self):
                return self.params.name

            @get('/cookies')
            @param('name', str, location='cookie')
            async def cookies_param(self):
                return self.params.name

        router.add(MainRouting)
        app.use(router)

        # url parameter
        res = TestClient(app).get('/url/1')
        assert res.text == '1'

        res = TestClient(app).get('/url/word')
        assert res.status == 400
        assert res.text == json.dumps({'id': 'cannot be converted to int'})

        # query parameter
        res = TestClient(app).get('/query?name=foo')
        assert res.text == 'foo'

        res = TestClient(app).get('/query')
        assert res.status == 400
        assert res.text == json.dumps({'name': 'miss parameter'})

        # form parameter
        res = TestClient(app).post('/post', data={'name': 'bar'})
        assert res.text == 'bar'

        res = TestClient(app).post('/post')
        assert res.status == 400
        assert res.text == json.dumps({'name': 'miss parameter'})

        # header parameter
        res = TestClient(app).get('/header', headers={'name': 'bars'})
        assert res.text == 'bars'

        res = TestClient(app).get('/header')
        assert res.status == 400
        assert res.text == json.dumps({'name': 'miss parameter'})

        # cookies parameter
        res = TestClient(app).get('/cookies', cookies={'name': 'bars'})
        assert res.text == 'bars'

        res = TestClient(app).get('/cookies')
        assert res.status == 400
        assert res.text == json.dumps({'name': 'miss parameter'})

    def test_multiple_location(self, app, router):

        class MainRouting(ResourceRouting):

            @post('/')
            @param('name', str, location=['query', 'form', 'header', 'cookie'])
            async def multiple_location(self):
                return self.params.name

        router.add(MainRouting)
        app.use(router)

        res = TestClient(app).post('/?name=foo')
        assert res.text == 'foo'

        res = TestClient(app).post('/', headers={'name': 'bar'})
        assert res.text == 'bar'

        res = TestClient(app).post('/', data={'name': 'foo'}, headers={'name': 'bar'})
        assert res.text == 'foo'

        res = TestClient(app).post('/')
        assert res.text == json.dumps({'name': 'miss parameter'})

    def test_optional_param_without_default(self, app, router):
        with pytest.raises(ParamNeedDefaultValueIfItsOptional):
            class MainRouting(ResourceRouting):
                @get('/')
                @param('name', str, optional=True)
                async def without_default(self):
                    return self.params.name

            router.add(MainRouting)
            app.use(router)

    def test_default_value(self, app, router):

        class MainRouting(ResourceRouting):
            @get('/')
            @param('name', str, optional=True, default='foo')
            async def multiple_location(self):
                return self.params.name

        router.add(MainRouting)
        app.use(router)

        res = TestClient(app).get('/?name=bar')
        assert res.text == 'bar'

        res = TestClient(app).get('/')
        assert res.text == 'foo'

    def test_warning(self, app, router):

        class MainRouting(ResourceRouting):
            @get('/')
            @param('name', str, warning='hello')
            async def multiple_location(self):
                return self.params.name

        router.add(MainRouting)
        app.use(router)

        res = TestClient(app).get('/?name=bar')
        assert res.text == 'bar'

        res = TestClient(app).get('/')
        assert res.text == json.dumps({'name': 'hello'})

    def test_action(self, app, router):

        class MainRouting(ResourceRouting):

            @get('/')
            @param('name', str, action='user')
            async def action(self):
                return self.params.user

        router.add(MainRouting)
        app.use(router)

        res = TestClient(app).get('/?name=123')
        assert res.text == '123'

    def test_append(self, app, router):

        class MainRouting(ResourceRouting):
            @get('/')
            @param('name', str, append=True)
            async def action(self):
                return self.params.name

        router.add(MainRouting)
        app.use(router)

        res = TestClient(app).get('/', params={'name': 'hello'})
        assert res.text == json.dumps(['hello'])

    def test_description(self, app, router):

        class MainRouting(ResourceRouting):
            @get('/')
            @param('name', str, description='the name of user')
            async def action(self):
                return self.params.name

        router.add(MainRouting)
        app.use(router)

        res = TestClient(app).get('/', params={'name': 'hello'})
        assert res.text == 'hello'

    def test_parameter_group(self, app, router):

        class Pagination(ParameterGroup):
            now = Param('now', int, optional=True, default=1)
            size = Param('size', int, optional=True, default=10)

        class MainRouting(ResourceRouting):

            @get('/list')
            @params(Pagination)
            async def show_list(self):
                return '{} {}'.format(self.params.now, self.params.size)

        router.add(MainRouting)
        app.use(router)

        res = TestClient(app).get('/list')
        assert res.text == '1 10'

        res = TestClient(app).get('/list', params={'now': 3})
        assert res.text == '3 10'

        res = TestClient(app).get('/list', params={'size': 5})
        assert res.text == '1 5'

        res = TestClient(app).get('/list', params={'now': 5, 'size': 15})
        assert res.text == '5 15'

    def test_multiple_parameters(self, app, router):

        class MainRouting(ResourceRouting):

            @get('/')
            @param('first_name', str)
            @param('last_name', str)
            async def hello(self):
                return f"hello {self.params.first_name} {self.params.last_name}"

        router.add(MainRouting)
        app.use(router)

        res = TestClient(app).get('/', params={'first_name': 'foo', 'last_name': 'bar'})
        assert res.text == 'hello foo bar'

    def test_parameter_redefine(self, app, router):
        with pytest.raises(ParamRedefineException):

            class MainRouting(ResourceRouting):

                @get('/')
                @param('name', str)
                @param('name', str)
                async def redefine(self):
                    return 'fine'

            router.add(MainRouting)
            app.use(router)

    def test_param_come_from_unknown_location(self, app, router):
        with pytest.raises(ParamComingFromUnknownLocation):
            class MainRouting(ResourceRouting):

                @get('/')
                @param('name', str, location='aaa')
                async def unknown(self):
                    return 'fine'

            router.add(MainRouting)
            app.use(router)


