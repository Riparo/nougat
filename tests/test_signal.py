import pytest
from nougat import Nougat, TestClient
from nougat.signal import Signal


class TestSignal:

    @pytest.mark.asyncio
    async def test_signal(self, app: Nougat,):
        v = []

        signal = Signal(app)

        @signal.listen('add')
        async def add(app):

            v.append('1')

        assert v == []

        await signal.activate('add')
        assert v == ['1']

    @pytest.mark.asyncio
    async def test_before_start_signal(self, app: Nougat, port: int):

        v = []

        @app.signal('before_start')
        async def test(app):
            v.append('1')

        async with TestClient(app, port) as client:
            assert v == ['1']


    @pytest.mark.asyncio
    async def test_after_start_signal(self, app: Nougat, port: int):

        v = []

        @app.signal('after_start')
        async def test(app):
            v.append('1')
            return v

        async with TestClient(app, port) as client:
            assert v == ['1']

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
            assert v == ['Hello', 'World']

        assert v == ['Hello', 'World']

    @pytest.mark.asyncio
    async def test_multiple_signal_sender(self, app: Nougat, port: int):
        v = []

        @app.signal('before_start')
        async def test(app):
            v.append('Hello')

        @app.signal('before_start')
        def test(app):
            v.append('World')

        async with TestClient(app, port) as client:
            assert set(v) == {'Hello', 'World'}

        assert set(v) == {'Hello', 'World'}

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
            assert v == ['Hello', 'World']

        assert v == ['Hello', 'World']
