import os, sys
from typing import Optional
from bs4.element import Tag

# hack
if sys.version_info < (3, 9):
    import gc
    from typing import (
        _GenericAlias as GenericAlias
    )
    for t in (list, dict, set, tuple, frozenset):
      r = gc.get_referents(t.__dict__)[0]
      r["__class_getitem__"] = classmethod(
          GenericAlias
      )

class Config:
    sentinel = object()
    def __init__(self):
        self.token = self.load_var("Token")
        self.prefix = self.load_var("Prefix", ".")
    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError as e:
            raise ValueError(
                f"Config variable {key!r} not loaded. \x0a"
                f"Perhaps you forgot to set a default "
                f"in `init.py`::`Config.__init__` using \x0a"
                f"`self.{key} = self.load_var("
                f"{key!r}, <DEFAULT>)`?"
            ) from e
    
    def load_from_envvar(self, key):
        return os.getenv(key)
    def load_from_dotenv(self, key):
        import dotenv
        return dotenv.get_key(
            dotenv_path=".env", key_to_get=key
        )
    
    def load_var(self, key, default_val=sentinel):
        for getter in (
            self.load_from_envvar, 
            self.load_from_dotenv
        ):
            val = getter(key)
            if val is None:
                continue
            if not val:
                warn(
                  f"Loading empty value for Config key"
                  f" {key!r} from {getter.__func__.__name__}"
                )
            return val
        # show error
        if default_val is not self.sentinel:
            return default_val
        return self.__getattr__(key)
Config = Config()

class Formatted:
    def __init__(self, fixed_part, formatted_paras, elem: Optional[Tag]=None):
        self.fixed_part = fixed_part
        self.formatted_paras = formatted_paras
        self.elem = elem
    
    def __str__(self):
        paras = "\n\n".join(self.formatted_paras)
        return f"{self.fixed_part.strip()}\x0A{paras.strip()}"