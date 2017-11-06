from nougat import Nougat
from nougat.routing import Routing, get
from nougat.test_client import TestClient


class TestBasicApplication:

    def test_asyncio(self):

        app = Nougat()

        class Basic(Routing):

            @get('/')
            async def index(self):
                return '123'

        app.route(Basic)

        res = TestClient(app).get('/')
        print(res)
        assert res.text == '123'
        res = TestClient(app).get('/')
        print(res)
        assert res.text == '123'
