
import sys, multiprocessing
from io import StringIO
import subprocess
calls = []

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
  calls.append((event,arg,*rest))
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
  if ("proc" in event or "thread" in event or "remove" in event or "del" in event or "hook" in event
  or "update" in event or "put" in event or "mk" in event
  or "rm" in event or "touch" in event or "make" in event
  or "set" in event or "shell" in event):
    raise Exception(f"Call to {event}{arg} disallowed")


if __name__ == "__main__":
  import builtins, sys
  sys.addaudithook(audit_hook)
  code = compile(sys.stdin.read(), "<eval command>", "exec")
  exec(code, {**builtins.__dict__, "__name__":"__maim__"})
  raise SystemExit(0)

class FakeStream(StringIO):
  
  def fileno(self):
    return 1


def run(src):
  # sio_stdout, sio_stderr = (StringIO(), StringIO())
  sio_stdout, sio_stderr = (FakeStream(), FakeStream())
  p = subprocess.run(
      ["timeout", "7s", sys.executable, __file__],
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
