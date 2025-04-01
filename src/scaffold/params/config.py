from types import SimpleNamespace
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader

from scaffold.params.envtag import EnvTag
Loader.add_constructor('!env', EnvTag.from_yaml)

class Config:

  @classmethod
  def get_config(cls, config_path, *, ns : bool):
    with open(config_path) as f:
      config = yaml.load(f, Loader=Loader)
      if ns:
        config = cls.as_namespace(config)
    return config

  @classmethod
  def as_namespace(cls, d):   
    obj = d
    if isinstance(d, list):
      dx = []
      for o in d:
        dx.append( cls.as_namespace(o) )
      obj = dx
    elif isinstance(d, dict):
      dx = {}
      for k,v in d.items():
        dx[k] = cls.as_namespace(v)
      obj = SimpleNamespace(**dx)  

    return obj

  @classmethod
  def as_dict(cls, ns):
    obj = ns
    if isinstance(ns, list):
      nsx = []
      for o in ns:
        nsx.append( cls.as_dict(o) )
      obj = nsx
    elif isinstance(ns, SimpleNamespace):
      dx = {}
      for k,v in vars(ns).items():
        dx[k] = cls.as_dict(v)
      obj = dx

    return obj

if __name__ == '__main__':
  config_path = "src/scaffold/samples/conf/basic.yaml"
  conf = Config.get_config(config_path, ns = True)

  d = Config.as_dict(conf)
  ns = Config.as_namespace(d)
  

  