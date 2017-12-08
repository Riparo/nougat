import pytest
import nougat
from nougat.router import Router


@pytest.fixture
def app():

    return nougat.Nougat()

@pytest.fixture
def router():
    return Router()
