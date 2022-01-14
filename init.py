import sys
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


class Formatted:
    def __init__(self, fixed_part, formatted_paras, elem: Optional[Tag]=None):
        self.fixed_part = fixed_part
        self.formatted_paras = formatted_paras
        self.elem = elem
    
    def __str__(self):
        paras = "\n\n".join(self.formatted_paras)
        return f"{self.fixed_part.strip()}\x0A{paras.strip()}"
