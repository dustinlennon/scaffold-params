import os, sys
from pathlib import Path

def _printf_debug(msg):
  if os.environ.get("PRINTF_DEBUG"):
    msg = f">>> {msg}"
    print(msg, file = sys.stderr)

# Define SCAFFOLD_PATH to support a wider range of configured
# sample scenarios.
import scaffold
os.environ.setdefault("SCAFFOLD_PATH", scaffold.__path__[0])
