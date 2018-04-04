from nougat.asgi import serve


async def http_serve(request):

    return 200, 'OK', [('content-type', 'plain-text')], 'hello world'


async def websocket_serve(connection):
    pass


serve(http_serve, websocket_serve)
