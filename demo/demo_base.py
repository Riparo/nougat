from misuzu import Misuzu, Section

app = Misuzu(__name__)

main = Section('main')


@main.get("/")
async def index_get(ctx):
    return "123"

@main.get("/123")
async def index(ctx):
    return "1233"

async def m(ctx, next):
    print(ctx.path)
    await next()

app.use(m)
app.use(main)

app.run(debug=True)
