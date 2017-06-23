import pytest
import json
from nougat import *
import aiohttp


def test_form_param():
    app = Nougat()
    main = Section("test")

    @main.post("/")
    @main.param("hello", str, location="form")
    async def index(ctx):
        return ctx.params.hello

    app.use(main)

    data = aiohttp.FormData()
    data.add_field("hello", "hello world")
    res, ctx = app.test.post("/", data=data)
    assert "hello world" == res.text

    data = aiohttp.FormData()
    data.add_field("hello", "中文测试")
    res, ctx = app.test.post("/", data=data)
    assert "中文测试" == res.text


def test_query_param():
    app = Nougat()
    main = Section("test")

    @main.get("/")
    @main.param("hello", str)
    async def index(ctx):
        return ctx.params.hello

    app.use(main)
    params = {'hello': 'hello world'}
    res, ctx = app.test.get("/", params=params)
    assert "hello world" == res.text

    params = {'hello': '中文测试'}
    res, ctx = app.test.get("/", params=params)
    assert "中文测试" == res.text


def test_cookies_param():
    app = Nougat()
    main = Section("test")

    @main.post("/")
    @main.param("hello", str, location="cookie")
    async def index(ctx):
        return ctx.params.hello

    app.use(main)

    res, ctx = app.test.post("/", cookies={"hello": 'helloworld', 'a': 'b'})
    assert "helloworld" == res.text


def test_header_param():
    app = Nougat()
    main = Section("test")

    @main.post("/")
    @main.param("hello", str, location="header")
    async def index(ctx):
        return ctx.params.hello

    app.use(main)

    res, ctx = app.test.post("/", headers={"Hello": 'helloworld', 'a': 'b'})
    assert "helloworld" == res.text


def test_form_params():
    app = Nougat()
    main = Section("test")

    @main.post("/")
    @main.param("param1", str, location="form")
    @main.param("param2", str, location="form")
    async def index(ctx):
        return [ctx.params.param1, ctx.params.param2]

    app.use(main)

    data = aiohttp.FormData()
    data.add_field("param1", "hello world")
    data.add_field("param2", "hello again")
    res, ctx = app.test.post("/", data=data)
    assert json.dumps(["hello world", "hello again"]) == res.text

    data = aiohttp.FormData()
    data.add_field("param1", "中文测试")
    data.add_field("param2", "hello again")
    res, ctx = app.test.post("/", data=data)
    assert json.dumps(["中文测试", "hello again"]) == res.text


def test_query_params():
    app = Nougat()
    main = Section("test")

    @main.get("/")
    @main.param("hello", str)
    @main.param("hello2", str)
    async def index(ctx):
        return {"hello": ctx.params.hello, "hello2": ctx.params.hello2}

    app.use(main)
    params = {'hello': 'hello world', 'hello2': "中文测试"}
    res, ctx = app.test.get("/", params=params)
    assert json.dumps({'hello': 'hello world', 'hello2': "中文测试"}) == res.text


def test_cookies_params():
    app = Nougat()
    main = Section("test")

    @main.post("/")
    @main.param("hello", str, location="cookie")
    @main.param("a", str, location="cookie")
    async def index(ctx):
        return {"hello": ctx.params.hello, "a": ctx.params.a}

    app.use(main)

    res, ctx = app.test.post("/", cookies={"hello": 'helloworld', 'a': 'b'})
    assert json.dumps({"hello": "helloworld", "a": "b"}) == res.text


def test_header_params():
    app = Nougat()
    main = Section("test")

    @main.post("/")
    @main.param("hello", str, location="header")
    @main.param("ccc", str, location="header")
    async def index(ctx):
        return [ctx.params.hello, ctx.params.ccc]

    app.use(main)

    res, ctx = app.test.post("/", headers={"Hello": 'helloworld', 'ccc': 'b'})
    assert json.dumps(["helloworld", 'b']) == res.text


def test_multiple_params():
    app = Nougat()
    main = Section("test")

    @main.post("/")
    @main.param("queryid", str, location="query")
    @main.param("formid", str, location="form")
    @main.param("cookieid", str, location="cookie")
    @main.param("headerid", str, location="header")
    async def index_get(ctx):
        return {
            "query_id": ctx.params.queryid,
            "form_id": ctx.params.formid,
            "cookie_id": ctx.params.cookieid,
            "header_id": ctx.params.headerid
        }

    app.use(main)
    params = {'queryid': 'query_hello', }
    headers = {"headerid": 'header_hello'}
    data = aiohttp.FormData()
    data.add_field("formid", "form_hello")
    cookies = {"cookieid": "cookie_hello"}
    res, ctx = app.test.post("/", params=params, headers=headers, cookies=cookies, data=data)
    assert json.dumps({
        "query_id": "query_hello",
        "form_id": "form_hello",
        "cookie_id": "cookie_hello",
        "header_id": "header_hello"
    }) == res.text


def test_param_load_from_second_location():
    app = Nougat()
    main = Section("test")

    @main.get("/")
    @main.param("hello", str)
    @main.param("hello2", str, location=['query', 'header'])
    async def index(ctx):
        return {"hello": ctx.params.hello, "hello2": ctx.params.hello2}

    app.use(main)

    params = {'hello': 'hello world', 'hello2': "hello"}
    res, ctx = app.test.get("/", params=params)
    assert json.dumps({'hello': 'hello world', 'hello2': "hello"}) == res.text

    params = {'hello': 'hello world'}
    headers = {'hello2': "hello"}
    res, ctx = app.test.get("/", params=params, headers=headers)
    assert json.dumps({'hello': 'hello world', 'hello2': "hello"}) == res.text


def test_optional_param():
    app = Nougat()
    main = Section("test")

    @main.get("/")
    @main.param("hello", str, optional=True)
    @main.param("hello2", str, location=['query', 'header'])
    async def index(ctx):
        return {"hello": ctx.params.hello, "hello2": ctx.params.hello2}

    app.use(main)

    params = {'hello2': "hello"}
    res, ctx = app.test.get("/", params=params)
    assert json.dumps({'hello': None, 'hello2': "hello"}) == res.text


def test_optional_and_default_param():
    app = Nougat()
    main = Section("test")

    @main.get("/")
    @main.param("hello", str, optional=True, default="hello aaa")
    @main.param("hello2", str, location=['query', 'header'])
    async def index(ctx):
        return {"hello": ctx.params.hello, "hello2": ctx.params.hello2}

    app.use(main)

    params = {'hello2': "hello"}
    res, ctx = app.test.get("/", params=params)
    assert json.dumps({'hello': "hello aaa", 'hello2': "hello"}) == res.text


def test_param_with_action():
    app = Nougat()
    main = Section("test")

    @main.get("/")
    @main.param("hello", str, action="world")
    async def index(ctx):
        return {"hello": ctx.params.world}

    app.use(main)

    params = {'hello': "hello"}
    res, ctx = app.test.get("/", params=params)
    assert json.dumps({'hello': "hello"}) == res.text


def test_append_param():
    app = Nougat()
    main = Section("test")

    @main.post("/")
    @main.param("hello", str, append=True)
    async def index(ctx):
        return {"hello": ctx.params.hello}

    @main.post("/diff-location")
    @main.param("hello", str, append=True, location=["query", 'cookie'])
    async def index_diff(ctx):
        return {"hello": ctx.params.hello}

    app.use(main)

    res, ctx = app.test.post("/?hello=1&hello=2")
    assert json.dumps({'hello': ["1", '2']}) == res.text

    res, ctx = app.test.post("/diff-location?hello=1&hello=2", cookies={"hello": "3"})
    assert json.dumps({'hello': ["1", '2', '3']}) == res.text
