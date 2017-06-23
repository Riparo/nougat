from nougat import Nougat, Section


def test_redirect():

    app = Nougat()
    main = Section("test")

    @main.get("/")
    async def test(ctx):
        ctx.redirect("/123")

    app.use(main)

    res, ctx = app.test.get("/")

    assert res.url == app.test.url("/123")
    assert res.status == 404
