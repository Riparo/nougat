from typing import TYPE_CHECKING, Callable, Any, List, Optional, Tuple, TypeVar, Type
import re
from nougat.exceptions import ParamRedefineException, ParamMissingException, RouteNoMatchException, HttpException
from nougat.parameter import Param
from functools import lru_cache
import logging

DYNAMIC_ROUTE_PATTERN = re.compile(r"(:(?P<name>[a-zA-Z_]+)(<(?P<regex>.+)>)?)+")


def __method_generator(method: str, route: str) -> Callable:

    def decorator(controller: (Callable, 'Route')) -> 'Route':

        if isinstance(controller, Route):
            controller.method = method
            controller.route = route
            return controller
        else:
            return Route(method, route, controller)

    return decorator


def get(route: str) -> Callable:

    return __method_generator('GET', route)


def post(route: str) -> Callable:

    return __method_generator('POST', route)


def patch(route: str) -> Callable:

    return __method_generator('PATCH', route)


def put(route: str) -> Callable:

    return __method_generator('PUT', route)


def delete(route: str) -> Callable:

    return __method_generator('DELETE', route)


class Route:

    def __init__(self, method: str, route: str, controller: Callable) -> None:
        self.method: str = method.upper()
        self.__route: str = route
        self.controller: Callable = controller
        self.params = {}

        self.__route_pattern_generator()

    def add_param(self,
                  name: str,
                  type: Callable[[str], Any],
                  location: (str, List[str]) = 'query',
                  optional: bool = False,
                  default: Any = None,
                  action=None,
                  append=False,
                  description: str = None
                  ) -> None:

        if name in self.params:
            raise ParamRedefineException(self.route, name)

        self.params[name] = Param(type, location, optional, default, action, append, description)

    def __route_pattern_generator(self):
        if self.__route:
            parameters: List[Tuple[str, str, str, str]] = DYNAMIC_ROUTE_PATTERN.findall(self.__route)
            parameters_pattern: List[Tuple[str, str]] = [(old, "(?P<{}>{})".format(name, pattern or '[^/]+')) for (old, name, _, pattern) in parameters]
            route_pattern: str = self.__route
            for old, param_pattern in parameters_pattern:
                route_pattern = route_pattern.replace(old, param_pattern)

            self.__route_pattern = re.compile(route_pattern)

    @property
    def route(self) -> str:
        return self.__route

    @route.setter
    def route(self, value):

        self.__route = value
        self.__route_pattern_generator()

    def match(self, method: str, route: str) -> bool:
        if self.method == method and self.__route_pattern.fullmatch(route):
            return True

        return False


class Routing:

    prefix: str = ''

    def __init__(self, request, response):
        self.request = request
        self.response = response

    def render(self) -> str:

        pass

    def redirect(self, url):
        """
        redirect to another page
        :param url: the page need to go
        """
        self.response.set_header("Location", url)
        self.abort(302)

    def abort(self, code: int, message: str = None) -> None:
        """
        abort HTTPException
        :param code: http status code
        :param message: http body
        """
        raise HttpException(code, message)

    def url_for(self, name, **kwargs):
        """
        get the url according to the section name and handler name
        :param name: a string like section_name.handler_name
        :return: the url string
        """
        # TODO url for function
        _name_split = name.split(".")

        if len(_name_split) != 2:
            raise Exception()  # TODO new exception

        section_name, handler_name = _name_split
        section = self.app.sections.get(section_name, None)

        if not section:
            raise Exception()  # TODO ne exception

        route = section.get_route_by_name(handler_name)

        return route.url(**kwargs)

    @classmethod
    def routes(cls) -> List[Route]:
        routes: List[Route] = []
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, Route):
                logging.debug("Routing {} has Route {} {}".format(cls.__class__, attr.method, attr.route))
                routes.append(attr)

        return routes


RoutingType = TypeVar('RoutingType', bound=Routing)


class Router:

    def __init__(self) -> None:
        self.__routes: List[Tuple[Type[RoutingType], 'Route']] = []

    @lru_cache(maxsize=2**5)
    def match(self, method: str, url: str) -> Optional[Tuple[Type[RoutingType], Route]]:
        """
        The Routes are divided into two types: Static Route and Dynamic Route
        For Static Route, it matches provided that the url is equal to the pattern
        For Dynamic Route, it will be converted to regex pattern when and only when it was registered to Router
        There are three types of Dynamic Route:
         - Unnamed Regex type: it is allowed to write regex directly in url, but it would not be called in controller functin
         - Simple type: it is the simplest way to identify a parameter in url using `:PARAM_NAME`, it would match fully character except /
         - Named Regex type: combining Simple type and Unnamed Regex Type, writing regex and give it a name for calling
        Router will return the first matching route
        :param method:
        :param url:
        :return:
        """
        for routing, route in self.__routes:
            if route.match(method, url):
                return routing, route

        raise RouteNoMatchException()

    def add_routing(self, routing: Type[RoutingType], route: 'Route') -> None:
        self.__routes.append((routing, route))
