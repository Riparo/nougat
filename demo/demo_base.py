from misuzu import Misuzu, Section

app = Misuzu(__name__)

main = Section('main')


@main.get("/")
async def index_get(ctx):
    return {"test": "hello world"}


app.use(main)

app.run(debug=True)
