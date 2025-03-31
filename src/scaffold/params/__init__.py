import os

# Define SCAFFOLD_PATH to support a wider range of configured
# sample scenarios.
import scaffold
os.environ.setdefault("SCAFFOLD_PATH", scaffold.__path__[0])
