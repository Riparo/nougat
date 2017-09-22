from nougat import Nougat
from nougat.routing import get, Routing

app = Nougat()


class CommonRouting(Routing):

    @get('/')
    def index(self):
        return 'hello world'

    @get('/user')
    def user_index(self):
        return 'hello user'


app.route(CommonRouting)

app.run(debug=True)
