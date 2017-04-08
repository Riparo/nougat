import re
from .response import Response

METHODS = ['HEAD', 'GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'PATCH', 'OPTIONS']


class Router:
    """
    路由系统
    """

    def __init__(self):

        self.fixed_routes = {}  # 静态路由
        self.dynamic_routes = {}  # 动态路由

        self.__init_route()
        self.__dynamic_pattern = re.compile(r"(<([a-zA-Z_]+)>)+")
        self.__default_route = StaticRoute("", self.__default)

    def __init_route(self):
        """
        初始化 静态路由、动态路由
        """
        for method in METHODS:
            self.fixed_routes[method] = {}
            self.dynamic_routes[method] = []

    def add(self, rule, handler, method, params):
        """
        添加路由
        :param rule: 路由规则
        :param handler: 处理方法
        :param method: 请求方法
        :param params: Param 列表
        """
        is_dynamic, match_pattern = self.__is_dynamic(rule)

        if is_dynamic:

            this_route = DynamicRoute(rule, handler, match_pattern)
            self.dynamic_routes[method].append(this_route)

        else:

            this_route = StaticRoute(rule, handler)
            self.fixed_routes[method][rule] = this_route

        for param in params:
            this_route.add_param(**param)

    def __is_dynamic(self, rule):
        """
        判断路由是否动态
        :param rule: 路由规则
        :return: boolean, formated_rule
        """
        match = self.__dynamic_pattern.findall(rule)
        if match:
            ret = rule
            for param in match:
                ret = ret.replace(param[0], "(?P<{}>[^/]+)".format(param[1]))
            return True, ret

        return False, rule

    @staticmethod
    async def __default(request):
        """
        默认路由，当找不到匹配项时触发
        :return:
        """
        return Response("404", status=404)

    def get(self, url, method):
        """
        寻找与 url 匹配的路由
        :param url: 目标 URL
        :param method: HTTP 访问方法
        :return: Route 类
        """

        # TODO refactor

        method = method.decode('utf-8')
        url = url.decode('utf-8')

        # try finding route in static map
        route = self.fixed_routes[method].get(url, None)

        if route is not None:
            return route

        else:
            # matching from dynamic routes

            for one_route in self.dynamic_routes[method]:
                if one_route.match(url):
                    return one_route

        if route is None:
            route = self.__default_route

        return route


class Param:

    def __init__(self, name, type, location=None, optional=False, default=None, action=None, append=False, description=None):
        self.name = name  # name
        self.type = type  # type or [type, type]
        self.location = location  # cookies, query, form, headers
        self.optional = optional  # true, false
        self.default = default  # if optional is true
        self.action = action  # rename
        self.append = append  # list or not
        self.description = description  # description

        # location iterable
        if not isinstance(self.location, list):
            self.location = [self.location]


class Route:
    """
    基本路由规则
    """
    rule = None
    handler = None
    params = []

    def add_param(self, name, type, **kwargs):
        """
        向规则中添加参数
        :param name:
        :param type:
        :param kwargs:
        :return:
        """
        self.params.append(Param(name, type, **kwargs))


class DynamicRoute(Route):
    """
    动态路由规则
    """

    def __init__(self, rule, handler, pattern):
        self.rule = rule
        self.handler = handler
        self.pattern = re.compile(pattern)
        self.params = []
        self.url_dict = {}

    def match(self, url):
        match = self.pattern.match(url)
        if match:
            if match.pos == 0 and match.endpos == len(url):
                self.url_dict = match.groupdict()
                return match

        return None


class StaticRoute(Route):
    """
    静态路由规则
    """
    def __init__(self, rule, handler):
        self.rule = rule
        self.handler = handler
        self.params = []
