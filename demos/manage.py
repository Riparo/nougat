from nougat import Nougat
from nougat.manage import Manager

app = Nougat()


async def middleware(response):

    response.content = 'Hello world'

app.use(middleware)


Manager(app).up()
