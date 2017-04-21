from misuzu import Misuzu
from misuzu.middleware import BaseMiddleware
from misuzu.section import Section
from time import time


class ResponseHeaderRecorder(BaseMiddleware):

    def __init__(self):
        super().__init__()
        self.__start_time = None

    def on_request(self, request):
        self.__start_time = time()

    def on_response(self, response):
        handle_time = time() - self.__start_time
        print("time: {}".format(handle_time))


class PrintURLOnRequest(BaseMiddleware):

    def __init__(self):
        super().__init__()

    def on_request(self, request):
        print("on request and url is {}".format(request.url))


app = Misuzu(__name__)
app.register_middleware(ResponseHeaderRecorder)
app.register_middleware(PrintURLOnRequest)

index = Section("index_test")

@index.get("/")
async def index_get(request):

    return {"hello": "hello"}

app.register_section(index)
app.run(debug=True)