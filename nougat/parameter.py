from typing import Callable, Any, List
from nougat.exceptions import ParamComingFromUnknownLocation


class Param:

    ALL_LOCATION = ['url', 'query', 'form', 'header', 'cookie']

    def __init__(self,
                 name: str,
                 type: Callable[[str], Any],
                 location: (str, List[str]) = None,
                 optional: bool =False,
                 default: Any =None,
                 action: str = None,
                 append: bool = False,
                 description: str = None):

        self.name = name
        self.type = type  # type or [type, type]
        self.location = location  # cookies, query, form, headers
        self.optional = optional  # true, false
        self.default = default  # if optional is true
        self.action = action  # rename
        self.append = append  # list or not
        self.description = description  # description
        if self.optional and not self.default:
            raise ValueError("if you set param optional, then type its default value")

        # location iterable
        if not isinstance(self.location, list):
            self.location = [self.location]
        unexpected_location = set(self.location) - set(Param.ALL_LOCATION)
        if unexpected_location:
            raise ParamComingFromUnknownLocation(self.name, unexpected_location)


class ParameterGroup:
    pass
