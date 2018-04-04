from nougat import Nougat
from nougat.router import Routing, get, Router, ResourceRouting, post, param
from nougat.test_client import TestClient
import asyncio

app = Nougat()
router = Router()

class Basic(ResourceRouting):

    @get('/1')
    async def index(self):
        return 'hello world'

    @post('/post')
    @param('name', str, location='form')
    async def form_param(self):
        return self.params.name


class MainRouting(Routing):

    @get('/')
    async def index(self):

        self.redirect('/after')

    @get('/after')
    async def redirect_after(self):

        return 'redirect after'

router.add(Basic)
router.add(MainRouting)
app.use(router)

app.run()