import asyncio
import httptools
from nougat.asgi.http import send_http_response, HTTPParser
from websockets import handshake, WebSocketCommonProtocol
from websockets.exceptions import ConnectionClosed

import functools

from typing import Tuple, Dict, List

MAX_RECEIVE_LENGTH: int = 2 ** 16


class SocketToHTTPParser:

    def __init__(self):
        self.headers: Dict[str, str] = {}
        self.url: str = ''
        self.body: bytes = b''
        self.completed = False

    def on_url(self, url: bytes):
        self.url = url.decode()

    def on_header(self, name: bytes, value: bytes):
        self.headers[name.decode()] = value.decode()

    def on_header_complete(self):
        pass

    def on_body(self, body: bytes):
        self.body += body

    def on_message_complete(self):
        self.completed = True


class SocketWrapper:

    def __init__(self, http_wrapper, websocket_wrapper):

        self.http = http_wrapper
        self.websocket = websocket_wrapper

    async def __call__(self, reader, writer):
        should_keep_alive = False

        while True:

            client_address = writer.get_extra_info('peername')
            http = True
            parser = SocketToHTTPParser()
            http_parser = httptools.HttpRequestParser(parser)

            while True:
                data = await reader.read(MAX_RECEIVE_LENGTH)

                try:
                    http_parser.feed_data(data)
                except httptools.HttpParserUpgrade:
                    http = False
                    break

                if not data or parser.completed:
                    break

            if http:

                # HTTP handler
                ret = await self.http({
                    'version': http_parser.get_http_version(),
                    'method': http_parser.get_method(),
                    'url': parser.url,
                    'headers': parser.headers,
                    'body': parser.body,
                    'ip': client_address[0]
                })
                if not (isinstance(ret, tuple) and len(ret) == 4):

                    writer.close()
                    raise Exception('no enough information for http response')

                http_code, code_info, headers, body = ret

                await send_http_response(writer, http_code, headers, body, http_status=code_info)

                if http_parser.should_keep_alive():
                    should_keep_alive = True
                else:
                    writer.close()

                if should_keep_alive:
                    continue

            else:

                # WebSocket handler
                headers = []
                key = handshake.check_request(lambda item: parser.headers.get(item))
                handshake.build_response(lambda k, v: headers.append((k, v)), key)

                await send_http_response(writer, 101, headers, b'', http_status='Switching Protocols')

                self.websocket_connection = WebSocketCommonProtocol()
                self.websocket_connection.client_connected(reader, writer)
                self.websocket_connection.connection_open()
                try:
                    await asyncio.sleep(3)
                    await self.websocket_connection.send("hello client")
                    while True:
                        echo = await self.websocket_connection.recv()
                        await self.websocket_connection.send('receive data {}'.format(echo))
                except ConnectionClosed:
                    await self.websocket_connection.close()

                writer.close()

                break
