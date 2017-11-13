from typing import Callable, Any, List, Optional, Tuple, TypeVar, Type, Set, Dict
import re
from nougat.exceptions import ParamRedefineException, RouteNoMatchException, HttpException
from nougat.parameter import Param
from functools import lru_cache


DYNAMIC_ROUTE_PATTERN = re.compile(r"(:(?P<name>[a-zA-Z_]+)(<(?P<regex>.+)>)?)+")


def __method_generator(method: str, route: str) -> Callable:

    def decorator(controller: (Callable, 'Route')) -> 'Route':

        if isinstance(controller, Route):
            controller.method = method
            controller.add_route(method, route)
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

        self.__route_prefix = ''

        self.__route: Set[Tuple[str, str]] = set()
        self.__route.add((method.upper(), route))

        self.controller: Callable = controller
        self.params = {}

        self.__route_pattern: List[Tuple[str, Any]] = []

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
            raise ParamRedefineException(" / ".join(self.route[1]), name)

        self.params[name] = Param(name, type, location, optional, default, action, append, description)

    def __route_pattern_generator(self):
        if self.__route:
            self.__route_pattern = []
            for method, route in self.__route:
                route = '{}{}'.format(self.__route_prefix, route)
                parameters: List[Tuple[str, str, str, str]] = DYNAMIC_ROUTE_PATTERN.findall(route)
                parameters_pattern: List[Tuple[str, str]] = [(old, "(?P<{}>{})".format(name, pattern or '[^/]+')) for (old, name, _, pattern) in parameters]
                route_pattern: str = route
                for old, param_pattern in parameters_pattern:
                    route_pattern = route_pattern.replace(old, param_pattern)

                self.__route_pattern.append((method, re.compile(route_pattern)))

    def set_prefix(self, prefix: str):
        self.__route_prefix = prefix

        self.__route_pattern_generator()

    @property
    def route(self) -> List[Tuple[str, str]]:
        return list(self.__route)

    def add_route(self, method: str, route: str):
        self.__route.add((method, route))

    def match(self, method: str, route: str) -> Tuple[bool, Optional[dict]]:
        for _method, pattern in self.__route_pattern:
            _match = pattern.fullmatch(route)
            if _method == method and _match:
                return True, _match.groupdict()

        return False, None


class Routing:

    prefix: str = ''

    def __init__(self, app, request, response, route: 'Route'):
        self.request = request
        self.response = response
        self._route = route
        self.app = app

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


    @classmethod
    def routes(cls) -> List[Route]:
        routes: List[Route] = []
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, Route):
                routes.append(attr)

        return routes

    async def handler(self, route: 'Route', controller):
        """
        let controller run through the middlewares of routing
        :param route: which route is this request
        :param controller: the controller function wrapped with `controller_result_to_response`
        :return:
        """

        return controller


RoutingType = TypeVar('RoutingType', bound=Routing)


class Router:

    def __init__(self) -> None:
        self.__routes: List[Tuple[Type[RoutingType], 'Route']] = []

    @lru_cache(maxsize=2**5)
    def match(self, method: str, url: str) -> Optional[Tuple[Type[RoutingType], Route, dict]]:
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
            is_match, url_dict = route.match(method, url)
            if is_match:
                return routing, route, url_dict

        raise RouteNoMatchException()

    def add_routing(self, routing: Type[RoutingType], route: 'Route') -> None:
        self.__routes.append((routing, route))
