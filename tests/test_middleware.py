import pytest
from nougat import Nougat, TestClient
from nougat.context import Request, Response
from nougat.exceptions import *


class TestMiddleware:

    @pytest.mark.asyncio
    async def test_no_middleware(self, app: Nougat, port: int):

        async with TestClient(app, port) as client:
            res = await client.get('/')

            assert res.text == ''

    @pytest.mark.asyncio
    async def test_middleware_with_no_param(self, app: Nougat, port: int):

        async def middleware():

            pass

        app.use(middleware)

        async with TestClient(app, port) as client:
            res = await client.get('/')

            assert res.text == ''

    @pytest.mark.asyncio
    async def test_middleware_with_all_params(self, app: Nougat, port: int):

        async def middleware(app, request, response: Response, next):

            response.code = 400
            response.content = 'Not Found'

        app.use(middleware)

        async with TestClient(app, port) as client:
            res = await client.get('/')

            assert res.text == 'Not Found'
            assert res.status == 400

    @pytest.mark.asyncio
    async def test_middleware_with_part_of_params(self, app: Nougat, port: int):
        async def middleware(response: Response, next):
            response.code = 200
            response.content = 'Hello world'

        app.use(middleware)

        async with TestClient(app, port) as client:
            res = await client.get('/')

            assert res.text == 'Hello world'
            assert res.status == 200

    @pytest.mark.asyncio
    async def test_middleware_chain(self, app: Nougat, port: int):
        async def middleware1(response: Response, next):

            await next()
            response.code = 200
            response.content = 'ret from 1'

        async def middleware2(response: Response, next):
            await next()
            response.code = 200
            response.content = 'ret from 2'

        app.use(middleware1, middleware2)

        async with TestClient(app, port) as client:
            res = await client.get('/')

            assert res.text == 'ret from 1'
            assert res.status == 200

    @pytest.mark.asyncio
    async def test_middleware_chain_stop_at_one_step(self, app: Nougat, port: int):
        async def middleware1(response: Response, next):
            await next()

        async def middleware2(response: Response, next):
            response.code = 200
            response.content = 'ret from 2'

        async def middleware3(response: Response, next):
            await next()
            response.code = 200
            response.content = 'ret from 3'

        app.use(middleware1, middleware2, middleware3)

        async with TestClient(app, port) as client:
            res = await client.get('/')

            assert res.text == 'ret from 2'
            assert res.status == 200

    @pytest.mark.asyncio
    async def test_middleware_must_be_async_function(self, app: Nougat):
        with pytest.raises(UnknownMiddlewareException,
                           match="Middleware m should be async function"):

            def m():
                pass

            app.use(m)

    @pytest.mark.asyncio
    async def test_middleware_params_out_of_boundary(self, app: Nougat):
        with pytest.raises(UnknownMiddlewareException):
            async def m(app, res, req):
                pass

            app.use(m)
