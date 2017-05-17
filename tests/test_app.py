from misuzu import Misuzu, Section
from misuzu.exceptions import MisuzuRuntimeError, UnknownSectionException
import json
import pytest


def test_use_not_section_instance():
    with pytest.raises(MisuzuRuntimeError):
        app = Misuzu("test")
        app.use(Misuzu())


def test_use_section():
    app = Misuzu("test")
    app.use(Section("test"))

    assert len(app.sections) == 1


def test_get():
    app = Misuzu()

    main = Section("main")

    @main.get("/")
    async def index(ctx):
        return "123"

    app.use(main)

    res, ctx = app.test.get("/")
    assert res.text == "123"


def test_post():
    app = Misuzu()

    main = Section("main")

    @main.post("/")
    async def index(ctx):
        return "1234"

    app.use(main)

    res, ctx = app.test.post("/")
    assert res.text == "1234"
