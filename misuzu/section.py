import inspect
from functools import partial
from misuzu.router import Router
from misuzu.exceptions import HandlerRedefineException, MisuzuRuntimeError
from misuzu.utils import is_middleware


__all__ = ['Section']


class Section:

    def __init__(self, name):
        self.name = name
        self.router = Router(self.name)
        self.__temper_params = []
        self.chain = []
        self.__handler = {}

    def __route(self, url, method):
        """
        添加路由
        :param url: 路由规则
        :param method: HTTP 访问方法
        """
        def response(handler):
            if handler.__name__ in self.__handler:
                raise HandlerRedefineException(self.name, handler.__name__)
            route = self.router.add(url, handler, self.name, method, self.__temper_params)
            self.__handler[handler.__name__] = route
            self.__temper_params = []  # reset temper params
            return handler
        return response

    def get_route_by_name(self, handler_name):
        """
        get route by its handler name
        """
        return self.__handler.get(handler_name, None)

    def head(self, url):
        return self.__route(url, "HEAD")

    def get(self, url):

        return self.__route(url, "GET")

    def post(self, url):

        return self.__route(url, "POST")

    def put(self, url):

        return self.__route(url, "PUT")

    def delete(self, url):

        return self.__route(url, "DELETE")

    def options(self, url):

        return self.__route(url, "OPTIONS")

    def patch(self, url):

        return self.__route(url, "PATCH")

    def param(self,  name, type, location='query', optional=False, default=None, action=None, append=False, description=None):
        """
        为路由添加参数
        :param name: 参数名称
        :param type:参数类型
        :param location: 参数来源
        :param optional: 参数是否可选
        :param default: 参数默认值，仅当 optional 为 True 时有效
        :param action: 参数重命名
        :param append: 参数是否为 list
        :param description: 参数描述
        """
        self.__temper_params.append(dict(name=name,
                                         type=type,
                                         location=location,
                                         optional=optional,
                                         default=default,
                                         action=action,
                                         append=append,
                                         description=description))

        def response(handler):

            return handler

        return response

    def use(self, middleware):
        """
        register Middleware
        """
        if inspect.isfunction(middleware):
                is_middleware(middleware)
                self.chain.insert(0, middleware)
        else:
            raise MisuzuRuntimeError("section only can use middleware function")

    async def handler(self, context, route):

        async def ret_handler(context, next):
            ret = await next()
            # TODO handle different type of ret: json, text, html
            context.res = ret

        handler = route.handler
        handler = partial(handler, ctx=context)
        handler = partial(ret_handler, context=context, next=handler)

        for middleware in self.chain:
            handler = partial(middleware, context=context, next=handler)

        await handler()
