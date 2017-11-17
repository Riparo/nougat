from typing import Callable, Any, List, Tuple, Dict, Any
from nougat.routing import Route, Routing
from nougat.parameter import Param, ParameterGroup
from nougat.exceptions import ParamCouldNotBeFormattedToTargetType
from nougat.utils import response_format


LOCATION_MAP = {
    'url': lambda request, key: request.url_dict.get(key, None),
    'query': lambda request, key: request.url.query.get(key, None),
    'form': lambda request, key: request.form.get(key, None),
    'header': lambda request, key: request.headers.get(key, None),
    'cookie': lambda request, key: request.cookies.get(key, None)
}


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
          description: str = None
          ) -> Callable:

    def decorator(controller: (Callable, 'Route')) -> 'Route':

        if not isinstance(controller, Route):
            controller = Route('', '', controller)

        controller.add_param(name, type,  location, optional, default, action, append, description)

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
            if not ret and param_info.optional:
                ret = [param_info.default]

            if not param_info.append:
                ret = [ret[0]]

            # verify the type of parameter
            try:

                ret = list(map(param_info.type, ret))

            except ParamCouldNotBeFormattedToTargetType as e:
                error_dict[name] = e.info

            _parameters[param_name] = (ret if param_info.append else ret[0])

        if not error_dict:

            for key, value in _parameters.items():
                self.params.__setattr__(key, value)

            return True, error_dict
        return False, error_dict

    async def handler(self, route: 'Route', controller):

        # format restful parameters

        is_pass, error_dict = self.__params_generator()

        if not is_pass:
            response_type, result = response_format(error_dict)
            self.response.status = 400
            self.response.type = response_type
            self.response.res = result

        else:
            await controller()
