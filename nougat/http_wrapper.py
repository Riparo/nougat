from socket import SHUT_WR
import curio
import h11
from typing import TYPE_CHECKING, List, Tuple
from nougat.context import Request

if TYPE_CHECKING:
    from nougat.context import Response

MAX_RECEIVE_LENGTH = 2 ** 16


class HTTPWrapper(object):
    """
    HTTP Wrapper, handle the event of connection
    """

    def __init__(self, sock, address):
        self.__sock = sock
        self.__address = address
        self.conn = h11.Connection(our_role=h11.SERVER)

    async def close(self):
        """
        close connection
        """

        with self.__sock.blocking() as real_sock:
            try:
                real_sock.shutdown(SHUT_WR)
            except OSError:
                # They're already gone, nothing to do
                return
        async with curio.ignore_after(3):
            try:
                while True:
                    # Attempt to read until EOF
                    got = await self.__sock.recv(MAX_RECEIVE_LENGTH)
                    if not got:
                        break
            finally:
                await self.__sock.close()

    async def send(self, event):
        """
        send message to client
        """
        assert type(event) is not h11.ConnectionClosed
        data = self.conn.send(event)
        await self.__sock.sendall(data)

    async def _read_from_peer(self):
        if self.conn.they_are_waiting_for_100_continue:
            await self.send(h11.InformationalResponse(status_code=100))
        try:
            data = await self.__sock.recv(MAX_RECEIVE_LENGTH)
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
                    async with curio.timeout_after(10):
                        event = await self.next_event()
                        if type(event) is h11.Request:

                            await self.handler(app, event)

                except curio.TaskTimeout:
                    # Time out Process
                    break

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
        method, target, headers, body = await self.request_parameters_generator(event)

        request: 'Request' = Request(app, target, dict(headers), self.__address[0], '1.1', method, body)
        response: 'Response' = await app.handler(request)

        await self.echo_response(response)

    async def request_parameters_generator(self, request):
        """
        load the information from request event
        :param request:
        :return: method, target, headers, body
        """
        method: str = request.method.decode("ascii")
        target: str = request.target.decode("ascii")
        headers: List[Tuple[str, str]] = [(name.decode("ascii"), value.decode("ascii"))
                                          for (name, value) in request.headers]
        body = ""
        while True:
            request = await self.next_event()
            if type(request) is h11.EndOfMessage:
                break

            if type(request) is not h11.Data:
                continue
            body += request.data.decode("ascii")

        return method, target, headers, body

    async def echo_response(self, response: 'Response'):
        """
        output the message of Response to client
        :param response: The Response instance coming from Nougat
        """
        response.output_generator()
        await self.send(h11.Response(status_code=response.status, headers=response.header_as_list))
        await self.send(h11.Data(data=response.output))
        await self.send(h11.EndOfMessage())
