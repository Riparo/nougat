import asyncio
import httptools
from websockets import handshake, WebSocketCommonProtocol
from websockets.exceptions import ConnectionClosed, InvalidHandshake

from nougat.context.request import Request

from typing import Callable, List, Tuple, Dict, Awaitable

MAX_RECEIVE_LENGTH: int = 2 ** 16
STATUS_CODES = {
    101: 'Switching Protocols',

    200: 'OK',
    201: 'Created',
    202: 'Accepted',

    301: 'Moved Permanently',
    302: 'Found',
    303: 'See Other',
    307: 'Temporary Redirect',
    308: 'Permanent Redirect',

    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Timeout',
    409: 'Conflict',
    451: 'Unavailable For Legal Reasons',

    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
    505: 'HTTP Version Not Supported',
    511: 'Network Authentication Required',

}

HTTP_WRAPPER_TYPE = Callable[[Request], Awaitable[Tuple[int, str, List[Tuple[str, str]], str]]]


class HTTPParser:
    """
    try to parse socket data as http protocol
    """

    def __init__(self) -> None:
        self.version: str = None
        self.method: bytes = None
        self.headers: Dict[str, str] = {}
        self.url: str = ''
        self.body: bytes = b''
        self.completed: bool = False

        self.raw_ip: str = ''

    def on_url(self, url: bytes) -> None:
        self.url = url.decode()

    def on_header(self, name: bytes, value: bytes) -> None:
        self.headers[name.decode()] = value.decode()

    def on_body(self, body: bytes) -> None:
        self.body += body

    def on_message_complete(self) -> None:
        self.completed = True


class SocketWrapper:
    def __init__(self,
                 http_wrapper: HTTP_WRAPPER_TYPE,
                 websocket_wrapper) -> None:

        self.http: HTTP_WRAPPER_TYPE = http_wrapper
        self.websocket = websocket_wrapper

    async def http_handle(self, data: HTTPParser, writer) -> None:

        # HTTP handler
        ret = await self.http(Request.load_from_parser(data))

        if not (isinstance(ret, tuple) and len(ret) == 4):
            writer.close()
            raise Exception('no enough information for http response')

        http_code, code_info, headers, body = ret

        await send_http_response(writer, http_code, headers, body, http_status=code_info)

    async def websocket_handle(self, data: HTTPParser, reader, writer) -> None:
        headers = []
        try:
            key = handshake.check_request(lambda item: data.headers.get(item))
            handshake.build_response(lambda k, v: headers.append((k, v)), key)
        except InvalidHandshake:
            await send_http_response(writer, 400, headers, b'Error on websocket handshake', http_status='Bad Request')

        else:
            await send_http_response(writer, 101, headers, b'', http_status='Switching Protocols')

            websocket_conn = WebSocketCommonProtocol()
            websocket_conn.client_connected(reader, writer)
            websocket_conn.connection_open()
            if self.websocket:
                try:
                    while True:
                        getter = websocket_conn.recv
                        sender = websocket_conn.send
                        await self.websocket(getter, sender)
                except ConnectionClosed:
                    await websocket_conn.close()
            else:
                await websocket_conn.close()

    async def __call__(self, reader, writer) -> None:

        while True:

            client_address = writer.get_extra_info('peername')
            http: bool = True
            parser: HTTPParser = HTTPParser()
            http_parser = httptools.HttpRequestParser(parser)

            while True:
                data: bytes = await reader.read(MAX_RECEIVE_LENGTH)

                try:
                    http_parser.feed_data(data)

                except httptools.HttpParserUpgrade:
                    http = False
                    break

                if not data or parser.completed:
                    break

            if http:

                parser.method = http_parser.get_method()
                parser.version = http_parser.get_http_version()
                parser.raw_ip = client_address[0]

                await self.http_handle(parser, writer)

                if http_parser.should_keep_alive():
                    continue
                else:
                    writer.close()

            else:

                await self.websocket_handle(parser, reader, writer)

                writer.close()
                break


async def send_http_response(writer,
                             http_code: int,
                             headers: List[Tuple[str, str]],
                             content: bytes,
                             http_status: str= None
                             ) -> None:
    """
    generate http response payload and send to writer
    """
    # generate response payload
    if not http_status:
        http_status = STATUS_CODES.get(http_code, 'Unknown')

    response: bytes = f'HTTP/1.1 {http_code} {http_status}\r\n'.encode()
    for k, v in headers:
        response += f'{k}: {v}\r\n'.encode()
    response += b'\r\n'
    response += content

    # send payload
    writer.write(response)
    await writer.drain()


async def serve(http_handler: HTTP_WRAPPER_TYPE,
                websocket_handler=None,
                address: str='127.0.0.1',
                port: int=8000):
    """
    start server
    """
    return await asyncio.start_server(SocketWrapper(http_handler, websocket_handler), address, port)
