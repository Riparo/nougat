import toml
import os
import re


env_pattern = "ENV::(?P<name>[a-zA-Z]+)::(?P<type>[A-Z]+)(::(?P<default>.*))?$"


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
        # error : "<name>'{}' is lowercase.".format(match.group('name'))
        # error : "<type>'{}' is out of list {}".format(match.group('type'), RARAM_GENERATOR.keys())
        if isinstance(value, str):
            match = re.match(env_pattern, value)
            if match:
                return True, match
        return False, None

    def get_env(self, match):
        ret = os.environ.get(match.group('name'), match.group('default'))
        if ret:
            into = PARAM_GENERATOR[match.group('type')]
            ret = into(ret)
            return ret

    def check_dict(self, value):
        if isinstance(value, dict):
            for each in value:
                is_environ, is_param = self.is_env(value[each])
                if is_environ:
                    value[each] = self.get_env(is_param)
                self.check_dict(value[each])

    def load(self, file):
        with open(file) as cfile:
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
# TODO load config from file and object
