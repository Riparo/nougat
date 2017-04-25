from misuzu import Misuzu, Section

app = Misuzu(__name__)

main = Section('main')


@main.get("/")
async def index_get(reqest):
    return {"test": "hello world"}

app.register_section(main)

app.run(debug=True)
