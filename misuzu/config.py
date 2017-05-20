import toml
import os
import re
from .utils import is_env_format
from .exceptions import ConfigException


env_pattern = "ENV::(?P<name>[0-9a-zA-Z]+)::(?P<type>[a-zA-Z]+)(::(?P<default>.*))?$"


class Config(dict):

    def __init__(self, default=None):
        super().__init__(default or {})

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError as e:
            raise AttributeError("{} do not exist".format(e.args[0]))

    def __setattr__(self, key, value):
        self[key] = value

    def is_env(self, value):
        """
        Judge the value adhere the format
        :param value: the value from the Config dict
        :return: (Boolean, match object)
        """
        if isinstance(value, str):
            match = re.match(env_pattern, value)
            if match:
                is_env_format(match, PARAM_GENERATOR)
                return True, match
        return False, None

    def get_env(self, match):
        """
        Get value from system environment variable
        if non-existent, setting the value to default
        and convert to variable type given
        :param match: the object returned by function re.match
        :return: 
        """
        ret = os.environ.get(match.group('name'), match.group('default'))
        if ret:
            into = PARAM_GENERATOR[match.group('type').upper()]
            ret = into(ret)
            return ret

    def check_dict(self, value):
        """
        Setting the value, if it conform the format
        :param value: the value from the Config dict
        :return: 
        """
        if isinstance(value, dict):
            for each in value:
                is_environ, is_param = self.is_env(value[each])
                if is_environ:
                    value[each] = self.get_env(is_param)
                self.check_dict(value[each])

    def use(self, name, func):
        """
        register the function
        :param name: key of dict
        :param func: custom function for transforming type of data
        :return: 
        """
        if PARAM_GENERATOR.get(name.upper(), None):
            raise ConfigException("function {}:{} exist".format(name, func.__name__))
        PARAM_GENERATOR[name.upper()] = func

    def load(self, file):
        """
        Traversing the dict from the toml file
        Set all value that conform to the format
        :param file: 
        :return: 
        """
        with open(file, 'r') as cfile:
            config = toml.loads(cfile.read())
        self.check_dict(config)
        self.update(config)


def into_str(value):
    if isinstance(value, str):
        return value
    return str(value)


def into_int(value):
    if isinstance(value, int):
        return value
    return int(value)


def into_bool(value):
    if isinstance(value, str):
        value = value.lower()
        if value == "true":
            return True
        return False
    return False

PARAM_GENERATOR = {
    'STR': into_str,
    'INT': into_int,
    'BOOL': into_bool
}
