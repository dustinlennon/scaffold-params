import os
import re
import yaml
# try:
#     from yaml import CLoader as Loader, CDumper as Dumper
# except ImportError:
#     from yaml import Loader

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

# Loader.add_constructor('!env', EnvTag.from_yaml)

# -- env_interpolate ---------------------------------------------------------------

def env_interpolate(s):
    regex = re.compile(r"\${(?P<name>.*?)}")

    matches = list(regex.finditer(s))

    r = s
    for m in matches[::-1]:
      r = r[0:m.start()] + os.environ.get(m['name'],"") + r[m.end():]

    return r
