import pytest
import nougat
from functools import partial
from nougat.router import Router


@pytest.fixture
@pytest.mark.asyncio
def app() -> 'nougat.Nougat':

    return nougat.Nougat()


@pytest.fixture
def router():
    return Router()


@pytest.fixture
@pytest.mark.asyncio
def port(unused_tcp_port) -> int:

    return unused_tcp_port
