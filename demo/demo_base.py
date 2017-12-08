from nougat import Nougat
from nougat.router import Routing
from nougat.router import get, post

app = Nougat()


class CommonRouting(Routing):

    @get('/')
    def index(self):
        return 'hello world'

    @get('/user')
    def user_index(self):
        return 'hello user'

    @get('/named/:id')
    def simple_type(self):
        return 'simple'

    @get('/user/:id<[0-9]+>')
    def named_regex_type(self):
        return 'named'

    @get('/.*')
    def unnamed_regex_type(self):
        return 'unnamed'


app.route(CommonRouting)

app.run(debug=True)
