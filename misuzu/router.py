import re
from .response import Response
from .exceptions import UnknownRouterException, RouteReDefineException
from .httpstatus import abort


__all__ = ['Router', 'Param', 'Route', 'DynamicRoute', 'StaticRoute']


METHODS = ['HEAD', 'GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'PATCH', 'OPTIONS']


class Router:
    """
    路由系统
    """

    def __init__(self, app_name):

        self.__app_name = app_name

        self.fixed_routes = {}  # 静态路由
        self.dynamic_routes = {}  # 动态路由
        self.handlers = {}

        self.__init_route()
        self.__dynamic_pattern = re.compile(r"(<([a-zA-Z_]+)>)+")
        self.__default_route = StaticRoute("", self.__default, self.__app_name)

    def __init_route(self):
        """
        初始化 静态路由、动态路由
        """
        for method in METHODS:
            self.fixed_routes[method] = {}
            self.dynamic_routes[method] = []

    def add(self, rule, handler, section_name, method, params):
        """
        添加路由
        :param rule: 路由规则
        :param handler: 处理方法
        :param section_name: the name of section
        :param method: 请求方法
        :param params: Param 列表
        """
        is_dynamic, match_pattern = self.__is_dynamic(rule)

        if is_dynamic:

            this_route = DynamicRoute(rule, handler, section_name, match_pattern)
            self.dynamic_routes[method].append(this_route)

        else:

            this_route = StaticRoute(rule, handler, section_name)
            self.fixed_routes[method][rule] = this_route

        self.handlers[handler.__name__] = this_route

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
        print("404")
        abort(404)

    def get(self, url, method):
        """
        寻找与 url 匹配的路由
        :param url: 目标 URL
        :param method: HTTP 访问方法
        :return: Route 类
        """

        # TODO refactor

        method = method
        url = url

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

    def url_for(self, route, method='GET', **kwargs):
        """
        寻找与路由匹配的 url
        :param route: 目标路由
        :param method: HTTP 访问方法
        :return: url
        """
        # r[0] : section name  r[1] : handler name
        r = re.split(r'\.', route)
        # count is used to determine whether to use '?' or '&' before params
        count = 0
        if self.handlers.get(r[1]) is not None:
            if self.handlers[r[1]].section_name == r[0]:
                ret = self.handlers[r[1]].rule

                # if rule is dynamic
                if self.__is_dynamic(ret)[0]:
                    match = self.__dynamic_pattern.findall(ret)
                    for key in kwargs:
                        if not isinstance(kwargs[key], str):
                            kwargs[key] = str(kwargs[key])
                        if match[0][1] == key:
                            ret = ret.replace(match[0][0], kwargs[key])
                        else:
                            if count == 0:
                                ret = ret + '?' + key + '=' + kwargs[key]
                            else:
                                ret = ret + '&' + key + '=' + kwargs[key]
                            count += 1
                    return ret

                # if rule is fixed
                else:
                    for key in kwargs:
                        if not isinstance(kwargs[key], str):
                            kwargs[key] = str(kwargs[key])
                        if count == 0:
                            ret = ret + '?' + key + '=' + kwargs[key]
                        else:
                            ret = ret + '&' + key + '=' + kwargs[key]
                        count += 1
                    return ret

                    # if url is None ,throw error

    def union(self, router):
        if not isinstance(router, Router):
            raise UnknownRouterException()

        for method in METHODS:

            # try get inner dict
            inter = [x for x in self.fixed_routes[method] if x in router.fixed_routes[method]]
            if inter:
                raise RouteReDefineException(method, inter[0])
            self.fixed_routes[method].update(router.fixed_routes[method])

            self.dynamic_routes[method].extend(router.dynamic_routes[method])

        self.handlers.update(router.handlers)

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
    section_name = ''

    def add_param(self, name, type, **kwargs):
        """
        向规则中添加参数
        """
        self.params.append(Param(name, type, **kwargs))


class DynamicRoute(Route):
    """
    动态路由规则
    """

    def __init__(self, rule, handler, section_name, pattern):
        self.rule = rule
        self.handler = handler
        self.section_name = section_name
        self.pattern = re.compile(pattern)
        self.params = []
        self.url_params_dict = {}

    def match(self, url):
        match = self.pattern.match(url)
        if match:
            if match.pos == 0 and match.endpos == len(url):
                self.url_params_dict = match.groupdict()
                return match

        return None


class StaticRoute(Route):
    """
    静态路由规则
    """
    def __init__(self, rule, handler, section_name):
        self.rule = rule
        self.handler = handler
        self.section_name = section_name
        self.params = []
