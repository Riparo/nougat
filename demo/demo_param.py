from misuzu import Misuzu, Section

app = Misuzu(__name__)
main = Section('main')

@main.get("/<name>")
@main.param('name', str)
async def index_get(request):
    return {'hello': request.params.name}

app.use(main)
app.run()
