from nougat import Nougat, Section

app = Nougat(__name__)
main = Section('main')

@main.get("/<name>")
@main.param('name', str)
async def index_get(request):
    return {'hello': request.params.name}

app.use(main)
app.run()
