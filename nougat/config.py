

__all__ = ['Config']


class Config(dict):

    def __init__(self):
        super().__init__({})

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            return None

    def __setattr__(self, key, value):
        self[key] = value
        return value

    def load_from_object(self, object_name):
        """
        load all upper parameters of object as config parameters
        :param object_name: the object you wanna load
        :return:
        """
        for key in dir(object_name):
            if key.isupper():
                self[key] = getattr(object_name, key)
