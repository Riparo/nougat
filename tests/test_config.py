import pytest
from misuzu import Misuzu
from misuzu.config import *
from misuzu.utils import *


def test_get_env(tmpdir):
    app = Misuzu("test")
    t = tmpdir.mkdir("sub").join("config.toml")
    t.write("home = 'ENV::HOME::STR'")
    app.config.load(t)
    p = os.environ.get("HOME")
    assert app.config['home'] == p


def test_nested_dict(tmpdir):
    app = Misuzu("test")
    t = tmpdir.mkdir("sub").join("config.toml")
    t.write("[a]\naa = 1\n[a.b]\nbb = 2")
    app.config.load(t)
    p = {
        'a': {'aa': 1, 'b': {'bb': 2}}
    }
    assert app.config == p


def test_no_env(tmpdir):
    app = Misuzu("test")
    t = tmpdir.mkdir("sub").join("config.toml")
    t.write("home = 'ENV::HOMES::STR::/'")
    app.config.load(t)
    assert app.config['home'] == "/"


def test_no_type(tmpdir):
    with pytest.raises(ConfigException):
        app = Misuzu("test")
        t = tmpdir.mkdir("sub").join("config.toml")
        t.write("home = 'ENV::HOME::SSS::/'")
        app.config.load(t)


def test_no_capitalized(tmpdir):
    with pytest.raises(ConfigException):
        app = Misuzu("test")
        t = tmpdir.mkdir("sub").join("config.toml")
        t.write("home = 'ENV::Home::STR::/'")
        app.config.load(t)


def test_exist_type_func():
    with pytest.raises(ConfigException):
        app = Misuzu("test")

        def into():
            pass
        app.config.use("STR", into)


def test_add_type(tmpdir):
    def double(value):
        return False, str(value)

    app = Misuzu("test")
    t = tmpdir.mkdir("sub").join("config.toml")
    t.write("home = 'ENV::HOME::DOUBLE::123'")
    app.config.use("DOUBLE", double)
    app.config.load(t)
    p = (False, os.environ.get("HOME", '123'))
    assert app.config == {'home': p}