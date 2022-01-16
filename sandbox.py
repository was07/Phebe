
class FakeStream(__import__("io").StringIO):
  
  def fileno(self):
    return 1


def _t():
  import types, sys
  from collections.abc import Mapping
  __sys_mod = sys.modules
  _ModDict__sys_mod = __sys_mod
  
  import subprocess
  def run(src):
    # sio_stdout, sio_stderr = (StringIO(), StringIO())
    sio_stdout, sio_stderr = (FakeStream(), FakeStream())
    
    p = subprocess.run(
        ["timeout", "0.5s", "env", "-i", sys.executable, __file__],
        input=src,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
    )
    try:
      p.check_returncode()
    except Exception as e:
      import traceback
      traceback.print_exc()
    
    rs = p.returncode
    output = sio_stdout.getvalue()
    errors = sio_stderr.getvalue()
    return (rs, p.stdout, p.stderr)
  run.sys = sys
  run.subprocess = subprocess

  class Default:
    def __bool__(self):
      return False
    def __eq__(self, other):
      return False
  
  __ = Default()
  def _raise(err: BaseException):
    raise err
  class ModDict(Mapping):
    def __init__(self):
      if False:
        t = __sys_mod
    def __getitem__(self, name, defv=__):
      if name in ("os", "sys"):
        raise Exception(f"Prohibited module {name}")
      mod = __sys_mod.get(name, __) or _raise(KeyError(name))
      if name == "os" or name == "sys":
        for i in range(5):
          if sys._getframe(i).f_code.co_filename[0] == "<":
            raise Exception(f"Prohibited module {name}")
      return mod
    def __setitem__(self, name, newv):
      if name in __sys_mod:
        for i in range(5):
          if sys._getframe(i).f_code.co_filename[0] == "<":
            raise Exception(f"Prohibited module reset: {name}")
        if isinstance(newv, types.ModuleType):
          #print(f"Overwriting sys.modules[{name!r}] "
          #      f"(={sys.modules[name]}) with "
          #      f"{newv=}")
          __sys_mod[name] = newv
          return
        raise Exception(f"Prohibited module reset ty: {name} {newv=}")
      __sys_mod[name] = newv
    def __delitem__(self, name):
      if name == "os" or name == "sys":
        raise Exception(f"Prohibited module delete: {name}")
      return None
    def __iter__(self):
      return iter()
    def items(self):
      return {k:v for k,v in __sys_mod.items() if k not in ("os", "sys") }.items()
    def keys(self):
      return {k:v for k,v in __sys_mod.items() if k not in ("os", "sys") }.keys()
    def values(self):
      return {k:v for k,v in __sys_mod.items() if k not in ("os", "sys") }.values()
    def get(self, name, *args):
      if name in ("os", "sys"):
        raise Exception(f"Prohibited module {name}")
      return __sys_mod.get(name, *args)
    def __len__(self):
      return len(__sys_mod)
    def pop(self, name):
      if name in ("os", "sys"):
        raise Exception(f"Prohibited module {name}")
      return __sys_mod.get(name,__ or None)
  
  def audit_hook(event, arg, *rest):
    if event in ("compile", "exec", "object.__getattr__"):
      return
    if event in ("object.__setattr__",):
      return
    if event in ("marshal.loads", "marshal.dumps"):
      return
    if event == "os.system":
      if arg[0] == b'(pager) 2>/dev/null':
        return
    if event == "subprocess.Popen":
      if arg[0] == '/bin/sh' and arg[1] == ['/bin/sh', '-c', 'pager']:
        return

    # print(f"{event=!r}, {arg=!r}")
    if event in ("sys.unraisablehook", "sys.excepthook"):
      return
    if event in ("open",):
      file, mode, *_ = arg
      if isinstance(file, int):
        return
      if set("w+a").intersection(mode):
        raise Exception(f"Writing to file {file!r} disallowed")
    if (event in "os.system"
    or event.startswith("os.") and (
      "exec" in event or "posix" in event or "kill" in event
      or "write" in event or "trace" in event or "run" in event
      or "put" in event or event.endswith("id")
    )):
      raise Exception(f"Call to {event}{arg} disallowed")
    if ("proc" in event or "thread" in event or "remove" in event or "del" in event or "sock" in event or "hook" in event
    or "update" in event or "put" in event or "mk" in event
    or "rm" in event or "touch" in event or "make" in event
    or "set" in event or "shell" in event or "os" in event or "sys" in event or "soc" in event):
      raise Exception(f"Call to {event}{arg} disallowed")
  
  global __name__
  if __name__ == "__main__":
    import builtins, sys
    sys.addaudithook(audit_hook)
    code = compile(sys.stdin.read(), "<eval command>", "exec")
    import builtins 




    #del __import__

    sys_modules = ModDict()
    try:
      del sys.modules["os"]
    except:
      pass
    try:
      del sys.modules["sys"]
    except:
      pass
    sys.modules = sys_modules
    try:
      del sys
    except:
      pass
    try:
      del os
    except:
      pass
    
    exec(code, {**builtins.__dict__, "__name__":"__maim__"})
    raise SystemExit(0)
  else:
    globals().__setitem__("run", run)

(_:=_t(), globals().__delitem__("_"))
