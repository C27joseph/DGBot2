from unidecode import unidecode


# FUNCTIONS

def clamp(value, vmin, vmax):
    if value < vmin:
        value = vmin
    elif value > vmax:
        value = vmax
    return vmin


def getKey(name: str) -> (str):
    return unidecode(str.lower(name))


# CLASSES
class KSingleton(object):
    _instances: dict = {}

    def __new__(cls, master):
        key = str(master.id)
        if not (key in cls._instances):
            cls._instances[key] = super().__new__(cls)
        return cls._instances[key]


class AliaseDict(dict):
    def __init__(self, *args, **kwargs):
        self.__aliases__ = {}
        self.__backup__ = {}
        super().__init__(*args, **kwargs)

    def __setitem__(self, key_aliases, value):
        key: str = getKey(key_aliases[0])
        aliases: list = key_aliases[1]
        self.__aliases__[key] = key
        self.__backup__[key] = aliases
        for alias in aliases:
            self.__aliases__[getKey(alias)] = key
        return super().__setitem__(key, value)

    def aliases(self, name) -> (list):
        key = getKey(name)
        key = self.__aliases__[key]
        return self.__backup__[key]

    def key(self, name) -> (str):
        key: str = getKey(name)
        return self.__aliases__[key]

    def exist(self, name):
        try:
            key = self.__aliases__[getKey(name)]
            return self.__contains__(key)
        except KeyError:
            return False

    def __getitem__(self, name):
        key: str = getKey(name)
        print("aliases, ", self.__aliases__)
        key = self.__aliases__[key]
        return super().__getitem__(key)

    def __delitem__(self, name):
        key = self.__aliases__[getKey(name)]
        del self.__backup__[key]
        return super().__delitem__(key)
