from nougat import Nougat
import pytest


@pytest.fixture
@pytest.mark.asyncio
def app() -> 'Nougat':

    return Nougat()


@pytest.fixture
@pytest.mark.asyncio
def port(unused_tcp_port) -> int:

    return unused_tcp_port
