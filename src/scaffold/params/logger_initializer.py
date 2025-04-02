import sys
import os
import time
from pathlib import Path

import logging
from logging.handlers import RotatingFileHandler

from scaffold.params.config import Config

class LoggerInitializer(object):
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

  def configure(self, logs_path, conf):
    self._configured  = True
    self._logs_path   = logs_path
    # self._config      = Config.as_dict(conf)
    self._loggers     = self._create_loggers(conf)

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

  def has_prefix(self, qualname, prefix):
    z = qualname.split(".")
    prefixes = [ ".".join(z[:i]) for i in range(len(z)+1) ]
    return prefix in prefixes

  def _create_loggers(self, conf):
    available = sorted(
      Config.as_dict(conf.loggers),
      key = lambda i: i.get("qualname", "")
    )
    
    loggers = {}
    for item in available:
      qualname    = item.get("qualname", "")
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

      loggers[qualname] = logger

    return loggers
 
  @classmethod
  def map_level(cls, name : str):
    level = getattr(logging, name)
    return level


if __name__ == '__main__':
  c = Config.get_config("src/scaffold/samples/conf/basic.yaml", ns = True)

  factory = LoggerInitializer()
  factory.configure(
    logs_path = "/tmp/scaffold-logs",
    conf = c.conf.logger
  )

  # As in `logging`, one should explictly create the root logger if
  # it is needed.
  root = factory()
  root.warning("from the root logger")

  main = factory("__main__")
  main.info("from the __main__ logger")
