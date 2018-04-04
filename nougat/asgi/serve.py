import asyncio
from nougat.asgi.socket import SocketWrapper


async def serve(http_handler, websocket_handler=None, address='127.0.0.1', port=8000):
    return await asyncio.start_server(SocketWrapper(http_handler, websocket_handler), address, port)
