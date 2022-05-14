from types import ModuleType
from typing import Dict, Any, List

__version__ = "0.0.1"



class NewAttr(object):
    """
    used instead of a NoneType in `__setattr__` and `_write_attr` so we can seperate `None` values, and new attributes.
    """ 
    pass

class NonWritable(Exception):
    pass


class Writable:
    def __init__(self, module: ModuleType, force: bool=False) -> None:
        self.module = module
        self._check(module, force)
        self._file = module.__file__
        self.sub: Dict[str, Any] = {}
        for x in dir(module):
            self.sub[x] = module.__dict__[x]

    @staticmethod
    def _check(module, force) -> bool:
        if module.__file__ == __file__ and force == False:
            raise NonWritable("that module can not be overwritten.")
        elif (not module.__file__.endswith(".py")) and (force == False):
            raise NonWritable("that module seems not to be a python file, are you sure you want to overwrite it?")
        else:
            return True
        

    def __getattribute__(self, name) -> Any:
        try:
            return object.__getattribute__(self, 'sub')[name]
        except (KeyError, AttributeError):
            try:
                return object.__getattribute__(self, name)
            except (KeyError, AttributeError):
                raise AttributeError()


    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self, 'sub'):
            try:
                old_val = self.sub[name]
            except KeyError:
                old_val = NewAttr()
            self.sub[name] = value
            self._write_attr(name, value, old_val)
            return
        object.__setattr__(self, name, value)


    def _write_attr(self, name, value, old_value) -> None:
        if isinstance(old_value, NewAttr):
            with open(self._file, 'r') as f:
                text: List[str] = f.readlines()
            text.append(f"{name} = {value}\n")
            with open(self._file, 'w') as f:
                f.writelines(text)
        else:
            with open(self._file, 'r') as f:
                text: List[str] = f.readlines()
            for line in text:
                if f"{name} = {old_value}" in line:
                    text[text.index(line)] = line.replace(f"{name} = {old_value}", f"{name} = {value}")
            with open(self._file, 'w') as f:
                f.writelines(text)