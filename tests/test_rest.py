import pytest
from nougat import Nougat, get, TestClient
from nougat.rest import ResourceRouting, param


class TestRestfulExtension:

    def test_parameter(self, app):

        class MainRouting(ResourceRouting):

            @get('/')
            @param('name', str)
            async def static_route(self):
                return 'hello {}'.format(self.params.name)

        app.route(MainRouting)

        res = TestClient(app).get('/?name=world')
        assert res.text == 'hello world'
