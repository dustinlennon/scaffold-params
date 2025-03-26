from typing import Optional

from abc import ABC

import os
import re
import argparse
import textwrap

from scaffold.params import _printf_debug
from scaffold.params.config import get_config
from scaffold.params.dotenv_reader import DotenvReader
from scaffold.params.exception_throwing_parser import ExceptionThrowingParser, ParserFallbackException

#- BaseParams -----------------------------------------------------------------

class BaseParams(ABC):
  _prefix : str 
  _opt_path : Optional[str] = None

  def __init__(self, config_path):
    """
    Dynamically create a parser with the following fallback semantics:
      - parser key
      - environment variable
      - YAML setting
    """

    cfg = get_config(config_path)

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

      env_name    = self.env_name(full_name)
      attr_name   = self.attr_name(name)
      flag_name   = self.flag_name(name)

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

    self.parser = parser

  @staticmethod
  def env_name(s):
    # alphanumeric, underscore, uppercased
    s = re.sub("-", "_", s)
    s = re.sub("[^_A-Za-z0-9]", "", s)
    return s.upper()

  @staticmethod
  def attr_name(s):
    # alphanumeric, underscore, lowercased
    s = re.sub("-", "_", s)
    s = re.sub("[^_A-Za-z0-9]", "", s)
    return s.lower()
  
  @staticmethod
  def flag_name(s):
    # alphanumeric, hyphenated, lowercased
    s = re.sub("_", "-", s)
    s = re.sub("[^-A-Za-z0-9]", "", s)
    return s.lower()

  def parse_args(self, args = None, namespace = None):
    args = self.parser.parse_args(args, namespace)
    self.assign_args(args)
    return args

  def assign_args(self, args):
    # the mixin hook
    # clsname = type(self).__name__; _printf_debug(f"{clsname}.assign_args()")
    super().assign_args(args)
    self.app_path = args.app_path

  @classmethod
  def build(cls):
    instance = None

    try:
      instance = cls.from_args(Parser = ExceptionThrowingParser)
    except ParserFallbackException as e:
      exit_args = (e.parser, 2, str(e))
    else:
      return instance

    try:
      instance = cls.from_env()
    except KeyError:
      pass
    else:
      return instance

    try:
      instance = cls.from_dotenv()
    except KeyError as e:
      argparse.ArgumentParser.exit(*exit_args)
    else:
      return instance


  @classmethod
  def from_args(cls, Parser = argparse.ArgumentParser):
    _printf_debug("searching for config: trying from_args()")
    parser = Parser()
    parser.add_argument("--config", required = True, help = "a yaml config file")

    args, _ = parser.parse_known_args()
    instance = cls(args.config)

    return instance

  @classmethod
  def from_env(cls):
    _printf_debug("searching for config: trying from_env()")
    env_name = f"{cls._prefix}_CONFIG_PATH"
    config = os.environ[env_name]
    instance = cls(config)
    return instance

  @classmethod
  def from_dotenv(cls):
    _printf_debug("searching for config: trying from_dotenv()")
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



