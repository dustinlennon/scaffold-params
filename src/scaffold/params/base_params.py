from typing import Optional

import os
import re
import argparse
import textwrap

from scaffold.params.base_mixin import BaseMixin
from scaffold.params.dotenv_reader import DotenvReader
from scaffold.params.exception_throwing_parser import ExceptionThrowingParser, ParserFallbackException
from scaffold.params.config import Config

#- BaseParams -----------------------------------------------------------------

class BaseParams(BaseMixin):
  _prefix : str 
  _opt_path : Optional[str] = None

  def __init__(self, config_path):
    """
    Dynamically create a parser with the following fallback semantics:
      - parser key
      - environment variable
      - YAML setting
    """

    cfg = Config.get_config(config_path, ns = True)

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    env_name = f"{self._prefix}_CONFIG_PATH"
    name = "<dotenv>"
    help = textwrap.dedent(f"""
    {env_name:<25} {name}
    '{config_path}'

    """).lstrip()
    parser.add_argument("--config", metavar="", help = help)

    for name, default_value in vars(cfg.env).items():
      full_name   = f"{self._prefix}_{name}"

      env_name    = self.map_env_name(full_name)
      attr_name   = self.map_attr_name(name)
      flag_name   = self.map_flag_name(name)

      value = os.environ.get(env_name, default_value)
      setattr(self, attr_name, value)

      help=textwrap.dedent(f"""
      {env_name:<25} env.{name}
      '{value}'

      """).lstrip()

      parser.add_argument(
        f"--{flag_name}",
        default = getattr(self, attr_name),
        metavar="",
        help=help
      )

    self._conf    = vars(cfg).setdefault("conf", dict())
    self._parser  = parser

  @staticmethod
  def map_env_name(s):
    # alphanumeric, underscore, uppercased
    s = re.sub("-", "_", s)
    s = re.sub("[^_A-Za-z0-9]", "", s)
    return s.upper()

  @staticmethod
  def map_attr_name(s):
    # alphanumeric, underscore, lowercased
    s = re.sub("-", "_", s)
    s = re.sub("[^_A-Za-z0-9]", "", s)
    return s.lower()
  
  @staticmethod
  def map_flag_name(s):
    # alphanumeric, hyphenated, lowercased
    s = re.sub("_", "-", s)
    s = re.sub("[^-A-Za-z0-9]", "", s)
    return s.lower()

  def _parse_args(self, args = None, namespace = None):
    args = self._parser.parse_args(args, namespace)
    self.assign_params(self._conf, args)
    self._args = args

  def assign_params(self, conf, args):
    # the mixin hook
    super().assign_params(conf, args)
    self.install_path = str(args.install_path)

  @classmethod
  def build(cls, args = None, namespace = None):
    instance = None

    try:
      instance = cls.from_args(Parser = ExceptionThrowingParser, args = args, namespace = namespace)
    except ParserFallbackException as e:
      exit_args = (e.parser, 2, str(e))
    else:
      instance._parse_args(args, namespace)
      return instance

    try:
      instance = cls.from_env()
    except KeyError:
      pass
    else:
      instance._parse_args(args, namespace)
      return instance

    try:
      instance = cls.from_dotenv()
    except KeyError as e:
      argparse.ArgumentParser.exit(*exit_args)
    else:
      instance._parse_args(args, namespace)
      return instance


  @classmethod
  def from_args(cls, Parser = argparse.ArgumentParser, args = None, namespace = None):
    parser = Parser()
    parser.add_argument("--config", required = True, help = "a yaml config file")

    args, _   = parser.parse_known_args(args, namespace)
    instance  = cls(args.config)

    return instance

  @classmethod
  def from_env(cls):
    env_name = f"{cls._prefix}_CONFIG_PATH"
    config = os.environ[env_name]
    instance = cls(config)
    return instance

  @classmethod
  def from_dotenv(cls):
    locs = [ p for p in 
      [
        cls._opt_path,
        'dotenv'
      ] if p
    ]

    key = f"{cls._prefix}_CONFIG_PATH"
    try:
      result = DotenvReader(locs).read()
    except FileNotFoundError:
      # treat a non-existing dotenv file like an empty dict
      raise KeyError(key)
    else:
      config_file = result[key]

    instance = cls(config_file)
    return instance


# if __name__ == '__main__':
#   import shlex
#   class Params(BaseParams):
#     _prefix = "PARAMS"

#   params = Params.build(
#     shlex.split("--config ./src/scaffold/samples/conf/basic.yaml")
#   )

