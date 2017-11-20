import pytest
import nougat


@pytest.fixture
def app():

    return nougat.Nougat()
