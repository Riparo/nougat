from nougat import Nougat
from nougat.routing import get, post, param, params, Param, ParameterGroup, Routing


app = Nougat()


class Pagination(ParameterGroup):

    page = Param(int)
    page_size = Param(int)


class CommonRouting(Routing):

    prefix = '/hello'

    @get('/:id')
    @param('name', str)
    def index(self):
        return 'hello'

    @get('/1')
    @params(ParameterGroup)
    def post_something(self):
        return 'got 1 now'


app.route(CommonRouting)

app.run(debug=True)
