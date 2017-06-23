from nougat import Nougat, Section
from nougat.exceptions import NougatRuntimeError, UnknownSectionException
import json
import pytest


def test_use_not_section_instance():
    with pytest.raises(NougatRuntimeError):
        app = Nougat("test")
        app.use(Nougat())


def test_use_section():
    app = Nougat("test")
    app.use(Section("test"))

    assert len(app.sections) == 1


def test_get():
    app = Nougat()

    main = Section("main")

    @main.get("/")
    async def index(ctx):
        return "123"

    app.use(main)

    res, ctx = app.test.get("/")
    assert res.text == "123"


def test_post():
    app = Nougat()

    main = Section("main")

    @main.post("/")
    async def index(ctx):
        return "1234"

    app.use(main)

    res, ctx = app.test.post("/")
    assert res.text == "1234"


def test_default_http_status():
    app = Nougat()
    main = Section("main")

    @main.get("/")
    async def index(ctx):
        return {"hello": "world"}

    app.use(main)

    res, ctx = app.test.get("/")
    assert res.status == 200
    assert res.text == json.dumps({"hello": "world"})


def test_client_http_status():
    app = Nougat()
    main = Section("main")

    @main.get("/")
    async def index(ctx):
        return {"hello": "world"}, 401

    app.use(main)

    res, ctx = app.test.get("/")
    assert res.status == 401