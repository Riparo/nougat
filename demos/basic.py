from nougat import Nougat

app = Nougat()


async def middleware(response):

    response.content = 'Hello world'

app.use(middleware)
app.run()
