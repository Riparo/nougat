from json import  dumps
from .httpstatus import STATUS_CODES

class Response:
    __slots__ = ('body', 'status', 'content_type')

    def __init__(self, body='', status=200, content_type='text/html'):
        self.content_type = content_type
        self.body = body
        self.status = status

    @property
    def body_bytes(self):
        body_type = type(self.body)
        if body_type is str:
            body = self.body.encode('utf-8')
        elif body_type is bytes:
            body = self.body
        else:
            body = b'Unable to interpret body'

        return body

    def output(self, version):
        body = self.body_bytes
        return b''.join([
            'HTTP/{} {} {}\r\n'.format(version, self.status, STATUS_CODES.get(self.status, 'FAIL')).encode('latin-1'),
            'Content-Type: {}\r\n'.format(self.content_type).encode('latin-1'),
            'Content-Length: {}\r\n'.format(len(body)).encode('latin-1'),
            b'\r\n',
            body
        ])


def text(body):
    return Response(body=body, content_type='text/plain; charset=utf-8')


def html(body):
    return Response(body=body, content_type='text/html; charset=utf-8')


def json(body):
    return Response(body=dumps(body), content_type='application/json')
