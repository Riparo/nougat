import pytest
from nougat import Nougat, TestClient
from nougat.exceptions import UnknownSignalException

class TestSignal:

    @pytest.mark.asyncio
    async def test_before_start_signal(self, app: Nougat, port: int):

        v = []

        @app.signal('before_start')
        async def test(app):
            v.append('1')

        async with TestClient(app, port) as client:
            pass

        assert v == ['1']

    @pytest.mark.asyncio
    async def test_after_start_signal(self, app: Nougat, port: int):

        v = []

        @app.signal('after_start')
        async def test(app):
            v.append('1')

        async with TestClient(app, port) as client:
            pass

        assert v == ['1']

    @pytest.mark.asyncio
    async def test_signals(self, app: Nougat, port: int):
        v = []

        @app.signal('before_start')
        async def test(app):
            v.append('Hello')

        @app.signal('after_start')
        async def test(app):
            v.append('World')

        async with TestClient(app, port) as client:
            pass

        assert v == ['Hello', 'World']

    @pytest.mark.asyncio
    async def test_multiple_signal_sender(self, app: Nougat, port: int):
        v = []

        @app.signal('before_start')
        async def test(app):
            v.append('Hello')

        @app.signal('before_start')
        async def test(app):
            v.append('World')

        async with TestClient(app, port) as client:
            pass

        assert v == ['Hello', 'World']

    @pytest.mark.asyncio
    async def test_sync_signal_sender(self, app: Nougat, port: int):
        v = []

        @app.signal('before_start')
        def test(app):
            v.append('Hello')

        @app.signal('after_start')
        def test(app):
            v.append('World')

        async with TestClient(app, port) as client:
            pass

        assert v == ['Hello', 'World']

    @pytest.mark.asyncio
    async def test_unknown_signal(self, app: Nougat):
        with pytest.raises(UnknownSignalException, match="can not add signal unknown"):

            @app.signal('unknown')
            def test(app):
                pass
