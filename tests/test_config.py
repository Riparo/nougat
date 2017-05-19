import pytest
from misuzu.config import *
from misuzu.utils import *


def test_get_env():
    c = Config()
    c.load("config.toml")
    p = os.environ.get("HOME")
    assert c['user']['path'] == p


def test_no_env():
    c = Config()
    c.load("config.toml")
    assert c['user']['name']['firstname'] == False
    assert c['user']['name']['secondname'] == "/"


def test_no_type():
    with pytest.raises(ConfigException):
        str = "ENV::HOME::SSS::DDD"
        match = re.match(env_pattern, str)
        if match:
            is_env_format(match, PARAM_GENERATOR)

def test_not_capitalized():
    with pytest.raises(ConfigException):
        str = "ENV::Home::STR::DDD"
        match = re.match(env_pattern, str)
        if match:
            is_env_format(match, PARAM_GENERATOR)