import os, sys

def _printf_debug(msg, prefix = ">>> "):
  if os.environ.get("PRINTF_DEBUG"):
    msg = f"{prefix}{msg}"
    print(msg, file = sys.stderr)
