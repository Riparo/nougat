from misuzu import Misuzu, Section

app = Misuzu(__name__)

main = Section('main')


@main.get("/")
async def index_get(request):
    return {"test": "hello world"}


@main.get("/<id>")
async def page(request):
    return {'page': app.router.url_for("main.page", id='abc', x=1, y=2)}


@main.get("/login")
async def login(request):
    app.redirect("/abc")

app.register_section(main)

app.run(debug=True)
