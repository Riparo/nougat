from misuzu import Misuzu, Section
import json


def test_app_get():
    app = Misuzu("first test")

    sec = Section("test")

    @sec.get("/")
    async def index(request):
        return {"hello": "world"}

    app.register_section(sec)

    request, response = app.test.get("/")

    assert request.url == '/'
    assert response.text == '{"hello": "world"}'

