from .router import Router
from .middleware import BaseMiddleware
from .exceptions import *


class Section:

    def __init__(self, name):
        self.name = name
        self.router = Router(self.name)
        self.__temper_params = []
        self.chains = []

    def __route(self, url, method):
        """
        添加路由
        :param url: 路由规则
        :param method: HTTP 访问方法
        """
        def response(handler):
            self.router.add(url, handler, method, self.__temper_params)
            self.__temper_params = []  # reset temper params
            return handler
        return response

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

    def register_middleware(self, middleware):
        """
        注册 Middleware
        :param middleware:
        :return:
        """
        if BaseMiddleware not in middleware.__bases__:
            raise UnknownMiddlewareException()

        self.chains.append(middleware)
