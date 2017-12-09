from typing import Callable, Any, List, Optional, Tuple, TypeVar, Type, Set, Dict, TYPE_CHECKING, Union
import re
from nougat.exceptions import ParamRedefineException, RouteNoMatchException, HttpException, \
    ResponseContentCouldNotFormat, \
    ParamNeedDefaultValueIfItsOptional, ParamComingFromUnknownLocation, ParamCouldNotBeFormattedToTargetType
from nougat.utils import response_format
from functools import lru_cache, partial
import logging

if TYPE_CHECKING:
    from nougat.context import Request, Response

__all__ = ['get', 'post', 'delete', 'put', 'patch',
           'Router', 'Routing',
           'ResourceRouting', 'Param', 'ParameterGroup', 'param', 'params']

LOCATION_MAP = {
    'url': lambda request, key: request.url_dict.get(key, None),
    'query': lambda request, key: request.url.query.get(key, None),
    'form': lambda request, key: request.form.get(key, None),
    'header': lambda request, key: request.headers.get(key, None),
    'cookie': lambda request, key: request.cookies.get(key, None)
}


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
                  location: Union[str, List[str]] = 'query',
                  optional: bool = False,
                  default: Any = None,
                  action=None,
                  append=False,
                  description: str = None,
                  warning: str = None
                  ) -> None:

        if name in self.params:
            raise ParamRedefineException(
                " / ".join(["{} {}".format(method, target) for method, target in list(self.__route)]),
                name
            )

        self.params[name] = Param(name, type, location, optional, default, action, append, description, warning)

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
    middleware: List[Callable] = []

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

    async def _handler(self, route: 'Route', controller):
        ret = await controller()
        self.response.content = ret

    async def handler(self, route: 'Route', controller):
        """
        let controller run through the middleware of routing
        :param route: which route is this request
        :param controller: the controller function
        :return:
        """
        handler = partial(self._handler, route=route, controller=controller)

        chain_reverse = self.middleware[::-1]
        for middleware in chain_reverse:
            handler = partial(middleware, context=self, next=handler)

        await handler()


class Param:

    ALL_LOCATION = ['url', 'query', 'form', 'header', 'cookie']

    def __init__(self,
                 name: str,
                 type: Callable[[str], Any],
                 location: (str, List[str]) = 'query',
                 optional: bool =False,
                 default: Any =None,
                 action: str = None,
                 append: bool = False,
                 description: str = None,
                 warning: str = None):

        self.name = name
        self.type = type  # type or [type, type]
        self.location = location  # cookies, query, form, headers
        self.optional = optional  # true, false
        self.default = default  # if optional is true
        self.action = action  # rename
        self.append = append  # list or not
        self.description = description  # description
        self.warning = warning
        if self.optional and not self.default:
            raise ParamNeedDefaultValueIfItsOptional()

        # location iterable
        if not isinstance(self.location, list):
            self.location = [self.location]
        unexpected_location = list(set(self.location) - set(Param.ALL_LOCATION))
        if unexpected_location:
            raise ParamComingFromUnknownLocation(self.name, unexpected_location)


class ParameterGroup:
    pass


class ParamDict(dict):

    def __init__(self):
        super().__init__()

    def __getattr__(self, item):
        return self.get(item, None)


def param(name: str,
          type: Callable[[str], Any],
          location: (str, List[str]) = 'query',
          optional: bool = False,
          default: Any = None,
          action=None,
          append=False,
          description: str = None,
          warning: str = None
          ) -> Callable:

    def decorator(controller: (Callable, 'Route')) -> 'Route':

        if not isinstance(controller, Route):
            controller = Route('', '', controller)

        controller.add_param(name, type,  location, optional, default, action, append, description, warning)

        return controller

    return decorator


def params(group: 'ParameterGroup') -> Callable:

    def decorator(controller: (Callable, 'Route')):
        if not isinstance(controller, Route):
            controller = Route('', '', controller)

        for attr_name in dir(group):
            attr = getattr(group, attr_name)
            if isinstance(attr, Param):
                controller.add_param(attr_name, attr.type, attr.location, attr.optional, attr.default, attr.action, attr.append, attr.description)

        return controller

    return decorator


class ResourceRouting(Routing):

    def __init__(self, app, request, response, route):
        super().__init__(app, request, response, route)

        self.params = ParamDict()

    def abort(self, code: int, message: str = None) -> None:
        pass

    def __params_generator(self) -> Tuple[bool, Dict[str, str]]:
        """
        format the params for resource
        """
        _parameters: Dict[str, Any] = {}
        error_dict: Dict[str, str] = {}
        for name, param_info in self._route.params.items():

            param_name = param_info.action or name

            ret = []

            # load
            for location in param_info.location:
                value_on_location = LOCATION_MAP.get(location)(self.request, name)
                if value_on_location:
                    if param_info.append:
                        if isinstance(value_on_location, list):
                            ret.extend(value_on_location)
                        else:
                            ret.append(value_on_location)
                    else:
                        if isinstance(value_on_location, list):
                            ret.append(value_on_location[0])
                        else:
                            ret.append(value_on_location)

            # set default value if optional is True and ret is empty
            if not ret:
                if param_info.optional:
                    ret = [param_info.default]
                else:
                    error_dict[name] = param_info.warning or 'miss parameter'
                    continue

            if not param_info.append:
                ret = [ret[0]]

            # verify the type of parameter
            try:

                ret = list(map(param_info.type, ret))

            except ParamCouldNotBeFormattedToTargetType as e:
                error_dict[name] = e.info

            except ValueError:
                error_dict[name] = 'cannot be converted to {}'.format(param_info.type.__name__)

            _parameters[param_name] = (ret if param_info.append else ret[0])

        if not error_dict:

            for key, value in _parameters.items():
                self.params.__setattr__(key, value)

            return True, error_dict
        return False, error_dict

    async def _handler(self, route: 'Route', controller):

        # format restful parameters

        is_pass, error_dict = self.__params_generator()

        if not is_pass:
            response_type, result = response_format(error_dict)
            self.response.status = 400
            self.response.type = response_type
            self.response.content = result

        else:
            ret = await controller()
            if isinstance(ret, tuple) and len(ret) == 2 and isinstance(ret[1], int):
                self.response.status = ret[1]
                ret = ret[0]
            response_type, result = response_format(ret)
            self.response.type = response_type
            self.response.content = result


RoutingType = TypeVar('RoutingType', bound=Routing)


class Router:

    __name__ = 'Nougat Router'

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

    def add(self, routing: Type[RoutingType]):
        """
        Register Routing class
        :param routing: Routing Class, not its instance
        :return:
        """
        logging.info('adding Routing {}'.format(routing.__class__))

        routing_prefix = routing.prefix

        for route in routing.routes():
            route.set_prefix(routing_prefix)
            self.__routes.append((routing, route))

    async def __call__(self, req: 'Request', res: 'Response', next: Callable):

        try:

            # match the Routing and Route from Router
            routing_class, route, url_dict = self.match(req.method, req.url.path)
            req.url_dict = url_dict
            routing = routing_class(self, req, res, route)

            handler = partial(route.controller, routing)

            handler = partial(routing.handler, route=route, controller=handler)

            await handler()

            # Formatting the Response data

        except ResponseContentCouldNotFormat:
            res.type = 'text/plain'
            res.content = "unable to format response"

        except RouteNoMatchException:
            res.status = 404
            res.type = 'text/plain'
            res.content = None

        await next()



