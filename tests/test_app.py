from misuzu import Misuzu
import json


def test_app_get():
    app = Misuzu("first test")

    @app.get("/")
    async def index(request):
        return {"hello": "world"}

    response = app.test.get("/")

    assert response.text == '{"hello": "world"}'

