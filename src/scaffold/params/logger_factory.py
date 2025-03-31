import sys
import os
import time
from pathlib import Path

import logging
from logging.handlers import RotatingFileHandler

from scaffold.params.config import get_config

class LoggerFactory(object):
  _state = None

  def __init__(self):
    if self._state:
      self.__dict__ = self._state
    else:
      self._initialize()

  def _initialize(self):
    self._handlers    = {}
    self._configured  = False

    formatter_args = {
      'style' : '{',
      'datefmt' : "%Y-%m-%d %H:%M:%S",
      'fmt' : "{asctime} | {name} | {levelname} | {message}"
    }
    formatter = logging.Formatter(**formatter_args)
    formatter.converter = time.gmtime

    self._formatter = formatter

    self._console_handler = logging.StreamHandler(sys.stderr)
    self._console_handler.setFormatter(self._formatter)    

    setattr(type(self), "_state", self.__dict__)

  def configure(self, config_file, logs_path):
    config = get_config(config_file, preprocess = False)
    self._configured  = True
    self._config      = config
    self._logs_path   = logs_path

  def assert_writable_logfile(self, logfile) -> str:
    p = Path(self._logs_path).joinpath(logfile).absolute()
    p.parent.mkdir(parents = True, exist_ok = True)

    with open(p, "a") as f:
      pass

    p.chmod(0o660)
    return str(p)

  def handler(self, logfile) -> logging.FileHandler:
    handler = self._handlers.get(logfile)
    if handler:
      return handler

    try:
      logfile = self.assert_writable_logfile(logfile)
    except (PermissionError, FileNotFoundError,) as e:
      handler = self._console_handler
    else:
      handler = RotatingFileHandler(logfile, maxBytes = 1e7, backupCount=3)
      self._handlers[logfile] = handler

    handler.setFormatter(self._formatter)
    return handler

  def __call__(self, qualname = None) -> logging.Logger:
    if self._configured == False:
      raise RuntimeError("LoggerFactory must call configure prior to instantiating loggers")

    items = [ item for item in self._config['loggers']
              if item.get("qualname") == qualname ]
    if len(items) == 0:
      raise AssertionError(f"{qualname} is not defined")
    elif len(items) > 1:
      raise AssertionError(f"{qualname} is defined multiple times")
    
    item  = items[0]

    logfile     = item.get("logfile")
    add_console = item.get("add_console", False)
    propagate   = item.get("propagate", True)
    level       = self.map_level(
                    item.get("level", "WARNING")
                  )

    logger = logging.getLogger(qualname)

    if logfile:
      handler = self.handler(logfile)
      
      if handler not in logger.handlers:
        logger.addHandler(handler)
    else:
      add_console = True

    if add_console:
      if self._console_handler not in logger.handlers:
        logger.addHandler(self._console_handler)    

    logger.propagate = propagate
    logger.setLevel(level)
    return logger
  
  @classmethod
  def map_level(cls, name : str):
    level = getattr(logging, name)
    return level


if __name__ == '__main__':
  factory = LoggerFactory()
  factory.configure(
    config_file = "src/scaffold/samples/conf/logger.yaml", 
    logs_path = "/tmp/scaffold-logs"
  )

  # As in `logging`, one should explictly create the root logger if
  # it is needed.
  root = factory()
  root.warning("from the root logger")

  main = factory("__main__")
  main.info("from the __main__ logger")
