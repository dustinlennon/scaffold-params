import os, sys

def _printf_debug(msg):
  if os.environ.get("PRINTF_DEBUG"):
    msg = f">>> {msg}"
    print(msg, file = sys.stderr)
