from misuzu import Misuzu, Section


def test_redirect():

    app = Misuzu()
    main = Section("test")

    @main.get("/")
    async def test(ctx):
        ctx.redirect("/123")

    app.use(main)

    res, ctx = app.test.get("/")

    assert res.url == app.test.url("/123")
