import pytest
from misuzu import Misuzu, Section, ParamRedefineException


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
