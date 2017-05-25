import pytest
from nougat import Nougat, Section
from nougat import HandlerRedefineException, NougatRuntimeError, RouteReDefineException


def test_section():
    pass


def test_repeat_section_name():
    with pytest.raises(NougatRuntimeError):
        app = Nougat()
        a = Section("a")
        b = Section("a")

        app.use(a)
        app.use(b)


def test_in_same_section_redefine_url():
    with pytest.raises(RouteReDefineException):
        app = Nougat()
        section = Section("section")

        @section.get("/")
        async def index(ctx):
            pass

        @section.get("/")
        async def indexs(ctx):
            pass

        app.use(section)


def test_in_diff_section_redefine_url():
    with pytest.raises(RouteReDefineException):
        app = Nougat()
        a = Section("a")
        b = Section("b")

        @a.get("/")
        async def index(ctx):
            pass

        @b.get("/")
        async def indexs(ctx):
            pass

        app.use(a)
        app.use(b)


def test_in_same_section_redefine_handler():
    with pytest.raises(HandlerRedefineException):
        app = Nougat()
        section = Section("section")

        @section.get("/")
        async def index(ctx):
            pass

        @section.get("/a")
        async def index(ctx):
            pass

        app.use(section)
