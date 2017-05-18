from misuzu import Misuzu, Section

app = Misuzu(__name__)

main = Section('context')


@main.get("/")
async def index_get(ctx):
    return "123"


@main.get("/123")
async def index(ctx):
    return ctx.url_for("context.index_get", a=1, b=2)


app.use(main)

app.run(debug=True)
