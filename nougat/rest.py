from typing import Callable, Any, List
from nougat.routing import Route, Routing
from nougat.parameter import Param, ParameterGroup
from nougat.utils import cached_property


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
        self.__params_generator()
        

    def abort(self, code: int, message: str = None) -> None:
        pass

    def __params_generator(self):
        """
        format the params for resource
        """
        print(self._route.params)
        for name, param_info in self._route.params.items():

            param_name = param_info.action or name

            ret = [] if param_info.append else None
            #
            # if is_dynamic and param_info.name in route.url_params_dict:
            #     self.params.__setattr__(param_name, route.url_params_dict[param_info.name])
            #     continue
            #
            # for location in param_info.location:
            #     location_value = self.__get_msg(location, param_info.name, param_info.append)
            #     if param_info.append:
            #         ret.extend(location_value)
            #     else:
            #         if not ret:
            #             ret = location_value
            #         else:
            #             break
            #
            # if not ret and param_info.optional:
            #     ret = param_info.default
            #
            # self.params.__set_param__(param_name, ret, param_info.type)

            self.params.__setattr__(param_name, ret)
