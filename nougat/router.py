import re
from nougat.exceptions import UnknownRouterException, RouteReDefineException, \
    ParamMissingException, ParamRedefineException


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

        self.__init_route()
        self.__dynamic_pattern = re.compile(r"(<([a-zA-Z_]+)>)+")

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
        is_dynamic, match_pattern, url_params = self.__is_dynamic(rule)

        if is_dynamic:
            this_route = DynamicRoute(rule, handler, section_name, match_pattern, url_params)

            # param missing check
            params_key = [param.name for param in params]
            x = [param for param in this_route.url_params if param not in params_key]
            if x:
                raise ParamMissingException(rule, x[0])

            self.dynamic_routes[method].append(this_route)

        else:

            this_route = StaticRoute(rule, handler, section_name)

            # raise rule redefine
            if rule in self.fixed_routes[method]:
                raise RouteReDefineException(method, rule)

            self.fixed_routes[method][rule] = this_route

        for param in params:
            this_route.add_param(**param)

        return this_route

    def __is_dynamic(self, rule):
        """
        判断路由是否动态
        :param rule: 路由规则
        :return: boolean, formated_rule
        """
        match = self.__dynamic_pattern.findall(rule)
        if match:
            ret = rule
            params = []
            for param in match:
                ret = ret.replace(param[0], "(?P<{}>[^/]+)".format(param[1]))
                if param[1] in params:
                    raise ParamRedefineException(rule, param[1])

                params.append(param[1])
            return True, ret, params

        return False, rule, None

    def get(self, context):
        """
        寻找与 url 匹配的路由
        :param context: request context
        :return: Route 类
        """

        method = context.method
        url = context.url.path

        # try finding route in static map
        route = self.fixed_routes[method].get(url, None)

        if route is not None:
            return route

        else:
            # matching from dynamic routes

            for one_route in self.dynamic_routes[method]:
                if one_route.match(url):
                    return one_route

        return route

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
    params = {}
    section_name = ''

    def add_param(self, name, type, **kwargs):
        """
        向规则中添加参数
        """
        if name in self.params:
            raise ParamRedefineException(self.rule, name)
        self.params[name] = Param(name, type, **kwargs)

    def url(self, **kwargs):
        pass


class DynamicRoute(Route):
    """
    动态路由规则
    """

    def __init__(self, rule, handler, section_name, pattern, url_params):
        self.rule = rule
        self.handler = handler
        self.section_name = section_name
        self.pattern = re.compile(pattern)
        self.params = {}
        self.url_params = url_params
        self.url_params_dict = {}

    def match(self, url):
        match = self.pattern.match(url)
        if match:
            if match.pos == 0 and match.endpos == len(url):
                self.url_params_dict = match.groupdict()
                return match

        return None

    def url(self, **kwargs):
        url_ret = self.rule
        for key, _ in self.url_params_dict.items():
            value = kwargs.get(key, None)
            if not value:
                _param = self.params.get(key, None)
                if _param:
                    value = _param.default


            if not value:
                raise Exception()  # TODO param miss exception

            url_ret = url_ret.replace("<{}>".format(key), value)
            kwargs.pop(key)

        if kwargs:
            url_ret = "{}?{}".format(url_ret, "&".join(["{}={}".format(key, value) for key, value in kwargs.items()]))

        return url_ret


class StaticRoute(Route):
    """
    静态路由规则
    """
    def __init__(self, rule, handler, section_name):
        self.rule = rule
        self.handler = handler
        self.section_name = section_name
        self.params = {}

    def url(self, **kwargs):
        url_ret = self.rule
        if kwargs:
            url_ret = "{}?{}".format(url_ret, "&".join(["{}={}".format(key, value) for key, value in kwargs.items()]))
        return url_ret
