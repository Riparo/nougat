class HTTPException(Exception):

    def __init__(self, body, status):
        self.body = body
        self.status = status
