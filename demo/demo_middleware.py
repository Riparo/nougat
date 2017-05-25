from nougat import Nougat, Section

async def request_header(ctx, next):

    # do whatever you want before handler
    await next(ctx)

    # do whatever you want after handler


app = Nougat(__name__)
app.use(request_header)

main = Section("main")


@main.get("/")
async def index(ctx):
    return {"hello": "world"}


app.run()
