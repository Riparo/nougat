import pytest
from misuzu import Misuzu, Section, ParamRedefineException, ParamMissingException


def test_parame():
    app = Misuzu()

    section = Section("section")

    @section.get("/")
    @section.param("hello", str)
    async def index(ctx):
        pass

    app.use(section)


def test_param_redefine():
    with pytest.raises(ParamRedefineException):
        app = Misuzu()

        section = Section("section")

        @section.get("/")
        @section.param("hello", str)
        @section.param("hello", str)
        async def index(ctx):
            pass

        app.use(section)


def test_param_missing():
    with pytest.raises(ParamMissingException):
        app = Misuzu()

        section = Section("section")

        @section.get("/<id>")
        async def index(ctx):
            pass

        app.use(section)
