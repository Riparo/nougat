from nougat import Nougat
from nougat.routing import Routing, get
from nougat.test_client import TestClient


class TestBasicApplication:

    def test_asyncio(self):

        app = Nougat()

        class Basic(Routing):

            @get('/')
            async def index(self):
                return '123'

        app.route(Basic)
        print("start running Test Case")
        res = TestClient(app).get('/')
        print(res)
        assert res.text == '123'

#
# def test_use_not_section_instance():
#     with pytest.raises(NougatRuntimeError):
#         app = Nougat("test")
#         app.use(Nougat())
#
#
# def test_use_section():
#     app = Nougat("test")
#     app.use(Section("test"))
#     print('有钱人')
#     assert len(app.sections) == 1
#
# def test_get():
#     app = Nougat()
#
#     main = Section("main")
#
#     @main.get("/")
#     async def index(ctx):
#         return "123"
#
#     app.use(main)
#
#     res, ctx = app.test.get("/")
#     assert res.text == "123"
#
#
# def test_post():
#     app = Nougat()
#
#     main = Section("main")
#
#     @main.post("/")
#     async def index(ctx):
#         return "1234"
#
#     app.use(main)
#
#     res, ctx = app.test.post("/")
#     assert res.text == "1234"
#
#
# def test_default_http_status():
#     app = Nougat()
#     main = Section("main")
#
#     @main.get("/")
#     async def index(ctx):
#         return {"hello": "world"}
#
#     app.use(main)
#
#     res, ctx = app.test.get("/")
#     assert res.status == 200
#     assert res.text == json.dumps({"hello": "world"})
#
#
# def test_client_http_status():
#     app = Nougat()
#     main = Section("main")
#
#     @main.get("/")
#     async def index(ctx):
#         return {"hello": "world"}, 401
#
#     app.use(main)
#
#     res, ctx = app.test.get("/")
#     assert res.status == 401
#
#
# @pytest.mark.asyncio
# async def test_asyncio(event_loop):
#     app = Nougat()
#
#     with app.create_server(event_loop):
#         print(123)
#
#     await asyncio.sleep(10)
#
#     assert 1 == 2
#
# # TODO: what will the test case looks like
# # @pytest.mask.asyncio
# # async def test_asyncio(loop_event):
# #
# #     app = Nougat()
# #
# #     await app.create_server(loop_event)
# #
# #     res = await app.get('fff')
# #
# #     assert res == 'hello'
#
#
# @pytest.mark.asyncio
# async def test_asyncio(event_loop):
#     app = Nougat()
#
#     app.create_server(event_loop)
#
#     await asyncio.sleep(10)
#
#     assert 1 == 2


app = Nougat()

class Basic(Routing):

    @get('/')
    async def index(self):
        return '123'

app.route(Basic)
print("start running Test Case")
res = TestClient(app).get('/')
print(res)
print(res.res_text)