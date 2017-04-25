__all__ = ['BaseMiddleware']


class BaseMiddleware:
    """
    the basic middleware model
    """

    def __init__(self):
        pass

    def on_request(self, request):
        pass

    def on_response(self, response):
        pass
