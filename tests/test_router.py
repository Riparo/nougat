import pytest
from nougat import Nougat, Section, ParamRedefineException, ParamMissingException


def test_parame():
    app = Nougat()

    section = Section("section")

    @section.get("/")
    @section.param("hello", str)
    async def index(ctx):
        pass

    app.use(section)


def test_param_redefine():
    with pytest.raises(ParamRedefineException):
        app = Nougat()

        section = Section("section")

        @section.get("/")
        @section.param("hello", str)
        @section.param("hello", str)
        async def index(ctx):
            pass

        app.use(section)


def test_param_missing():
    with pytest.raises(ParamMissingException):
        app = Nougat()

        section = Section("section")

        @section.get("/<id>")
        async def index(ctx):
            pass

        app.use(section)
