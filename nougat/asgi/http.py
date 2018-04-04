from typing import Dict, List, Tuple


class HTTPParser:

    def __init__(self):
        self.headers: Dict[str, str] = {}
        self.url: str = ''
        self.body: bytes = b''
        self.completed: bool = False

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


async def send_http_response(writer, http_code: int, headers: List[Tuple[str, str]], content: bytes, http_status: str= 'OK'):

    # generate response payload
    response: bytes = f'HTTP/1.1 {http_code} {http_status}\r\n'.encode()
    for k, v in headers:
        response += f'{k}: {v}\r\n'.encode()
    response += b'\r\n'
    response += content

    # send payload
    writer.write(response)
    await writer.drain()
