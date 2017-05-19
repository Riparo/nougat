import os
from misuzu.config import Config


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