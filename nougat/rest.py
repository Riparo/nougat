from typing import Callable, Any, List
from nougat.routing import Route, Routing
from nougat.parameter import Param, ParameterGroup
from nougat.utils import cached_property


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

    def abort(self, code: int, message: str = None) -> None:
        pass

    @cached_property
    def params(self):
        pass
