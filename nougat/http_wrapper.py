import h11
from typing import TYPE_CHECKING, List, Tuple
from nougat.context import Request
from nougat.utils import ConsoleColor
import datetime
import asyncio

if TYPE_CHECKING:
    from nougat.context import Response

MAX_RECEIVE_LENGTH = 2 ** 16


class HTTPWrapper(object):
    """
    HTTP Wrapper, handle the event of connection
    """

    def __init__(self, sock, address):
        self.__reader, self.__writer = sock
        self.__address = address
        self.conn = h11.Connection(our_role=h11.SERVER)

    async def close(self):
        """
        close connection
        """

        self.__writer.close()

    async def send(self, event):
        """
        send message to client
        """
        assert type(event) is not h11.ConnectionClosed
        data = self.conn.send(event)
        self.__writer.write(data)
        await self.__writer.drain()

    async def _read_from_peer(self):
        if self.conn.they_are_waiting_for_100_continue:
            await self.send(h11.InformationalResponse(status_code=100))
        try:
            data = await self.__reader.read(MAX_RECEIVE_LENGTH)
        except ConnectionError:
            # They've stopped listening. Not much we can do about it here.
            data = b""
        self.conn.receive_data(data)

    async def next_event(self):
        while True:
            event = self.conn.next_event()
            if event is h11.NEED_DATA:
                await self._read_from_peer()
                continue
            return event

    async def process(self, app):
        """
        THe process of handling
        :param app: The Nougat instance
        """
        while True:
            if self.conn.our_state == h11.IDLE and self.conn.their_state == h11.IDLE:

                try:
                    event = await asyncio.wait_for(self.next_event(), timeout=10)
                except asyncio.TimeoutError:
                    # Time out Process
                    break
                else:
                    if type(event) is h11.Request:
                        await self.handler(app, event)

            elif self.conn.our_state == h11.DONE and self.conn.their_state == h11.DONE:
                # reuse the connection
                try:
                    self.conn.start_next_cycle()
                except h11.ProtocolError:
                    break

            else:
                break

        await self.close()

    async def handler(self, app, event):
        """
        The real handler for real http request
        :param app: The Nougat Instance
        :param event: Request Event
        """
        start_time = datetime.datetime.now()

        method, target, headers, body = await self.request_parameters_generator(event)

        request: 'Request' = Request(app, target, dict(headers), self.__address[0], '1.1', method, body)
        response: 'Response' = await app.handler(request)

        response_status = await self.echo_response(response)

        if app.debug:
            handle_time = int((datetime.datetime.now()-start_time).total_seconds() * 10000)/10
            print('%s %15s   %12s %14sms   [%s]\t%s' % (
                start_time.strftime('%Y/%m/%d %I:%M:%S'),
                ConsoleColor.yellow(method.upper()),
                ConsoleColor.blue(str(response_status)) if 199 < response_status <= 400 else ConsoleColor.red(str(response_status)),
                ConsoleColor.green(str(handle_time)),
                self.__address[0],
                ConsoleColor.bold(target)
            ))

    async def request_parameters_generator(self, request) -> Tuple[str, str, List[Tuple[str, str]], bytes]:
        """
        load the information from request event
        :param request:
        :return: method, target, headers, body
        """
        method: str = request.method.decode("ascii")
        target: str = request.target.decode("ascii")
        headers: List[Tuple[str, str]] = [(name.decode("ascii"), value.decode("ascii"))
                                          for (name, value) in request.headers]
        body = b''
        while True:
            request = await self.next_event()
            if type(request) is h11.EndOfMessage:
                break

            if type(request) is not h11.Data:
                continue
            body += request.data

        return method, target, headers, body

    async def echo_response(self, response: 'Response') -> int:
        """
        output the message of Response to client
        :param response: The Response instance coming from Nougat
        """
        response.output_generator()
        await self.send(h11.Response(status_code=response.status, headers=response.header_as_list))
        await self.send(h11.Data(data=response.output))
        await self.send(h11.EndOfMessage())

        return response.status
