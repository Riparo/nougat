from nougat import Nougat
from nougat.routing import get, post, param, params, Param, ParameterGroup, Routing


app = Nougat()


class Pagination(ParameterGroup):

    page = Param(int)
    page_size = Param(int)


class CommonRouting(Routing):

    @get('/')
    @param('name', str)
    def index(self):
        return "hello"

    @post('/')
    @params(ParameterGroup)
    def post_something(self):
        return 'post'


app.route(CommonRouting)

app.run()