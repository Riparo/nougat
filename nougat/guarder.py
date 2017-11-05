from nougat.utils import get_all_parameters, call
from nougat.exceptions import GuarderDoesNotExist
from functools import partial
from contextlib import contextmanager


class GuarderManager:

    def __init__(self):
        self.__guarders = {}

    def guard(self, item, name=None):
        if not name:
            name = item.__name__

        self.__guarders[name] = item

    async def generator(self, func):
        args = get_all_parameters(func)

        for arg in args:
            if arg == "self":
                continue

            sub_guarder = self.__guarders.get(arg, None)
            if not sub_guarder:
                raise GuarderDoesNotExist(arg)

            sub_guarder = await self.__generator(sub_guarder)

            func = partial(func, **{arg: sub_guarder})
        return func

    async def __generator(self, guarder):
        args = get_all_parameters(guarder)
        for arg in args:
            sub_guarder = self.__guarders.get(arg, None)
            if not sub_guarder:
                raise GuarderDoesNotExist(arg)
            if arg not in ['app', 'context']:
                sub_guarder = await self.__generator(sub_guarder)

            guarder = partial(guarder, **{arg: sub_guarder})

        return await call(guarder)

    @contextmanager
    def guard_context(self, context):
        self.guard(context, "context")
        try:
            yield self
        finally:
            self.__guarders.__delitem__("context")

