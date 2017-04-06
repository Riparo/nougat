from .exceptions import HTTPException


__all__ = ()

STATUS_CODES = {
    200: 'OK',
    404: 'Not Found'
}

def abort(status, body=None):
    if not body:
        body = STATUS_CODES.get(status, "User Definition Code")
    raise HTTPException(body, status)

