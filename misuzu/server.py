import asyncio

from .protocol import HttpProtocol

uvloop = asyncio


def serve(router, host, port, debug=False):
    # Create Event Loop
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.set_debug(debug)

    server_coroutine = loop.create_server(lambda: HttpProtocol(loop=loop, router=router), host, port)
    server_loop = loop.run_until_complete(server_coroutine)
    try:
        print("run forever")
        loop.run_forever()
    except KeyboardInterrupt:
        print("ctrl+c")
        server_loop.close()
        loop.close()