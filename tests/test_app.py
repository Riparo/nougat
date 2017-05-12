from misuzu import Misuzu, Section
from misuzu.exceptions import MisuzuRuntimeError, UnknownSectionException
import json
import pytest


def test_use_not_section_instance():
    with pytest.raises(MisuzuRuntimeError):
        app = Misuzu("test")
        app.use(Misuzu())


def test_use_section():
    app = Misuzu("test")
    app.use(Section("test"))

    assert len(app.sections) == 1
