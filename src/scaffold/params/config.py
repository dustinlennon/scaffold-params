from types import SimpleNamespace
import os
import re
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader

# -- EnvTag -------------------------------------------------------------------
class EnvTag(yaml.YAMLObject):
  yaml_tag = u"!env"

  def __init__(self, s):
    self.s = s

  def __str__(self):
    return env_interpolate(self.s)

  def __repr__(self):
    return f'EnvTab("{self.s}")'

  @classmethod
  def from_yaml(cls, loader, node):
    return EnvTag(node.value)

Loader.add_constructor('!env', EnvTag.from_yaml)

# -- env_interpolate ---------------------------------------------------------------

def env_interpolate(s):
    regex = re.compile(r"\${(?P<name>.*?)}")

    matches = list(regex.finditer(s))

    r = s
    for m in matches[::-1]:
      r = r[0:m.start()] + os.environ.get(m['name'],"") + r[m.end():]

    return r

# -- get_config --------------------------------------------------------------------

def get_config(config_path, preprocess = True):
  with open(config_path) as f:
    config = yaml.load(f, Loader=Loader)
    if config is not None and preprocess:
      config = _as_namespace(config)
  return config

def _as_namespace(d):
  
  obj = d
  if isinstance(d, list):
    dx = []
    for o in d:
      dx.append( _as_namespace(o) )
    obj = dx
  elif isinstance(d, dict):
    dx = {}
    for k,v in d.items():
      dx[k] = _as_namespace(v)
    obj = SimpleNamespace(**dx)

  return obj


if __name__ == '__main__':
  config_path = "src/scaffold/samples/conf/basic.yaml"
  conf = get_config(config_path)
  
  # s = "${SCAFFOLD_PATH}/samples/conf/logger.yaml"
  # print(env_interpolate(s))

#   etab = EnvTag(s)

  