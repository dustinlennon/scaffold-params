import sys
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
    self._handlers  = {}
    self._config    = None

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

  def configure(self, config_file):
    config = get_config(config_file, preprocess = False)
    self._config = config

  def handler(self, logfile):
    handler = self._handlers.get(logfile)
    if handler:
      return handler

    try:
      p = Path(logfile).absolute()
      p.parent.mkdir(exist_ok = True)
    except (PermissionError,) as e:
      handler = self._console_handler
    else:
      handler = RotatingFileHandler(logfile, maxBytes = 1e7, backupCount=3)
      self._handlers[logfile] = handler

    handler.setFormatter(self._formatter)
    return handler

  def __call__(self, qualname = None) -> logging.Logger:
    if self._config is None:
      raise RuntimeError("LoggerFactory must call configure prior to instantiating loggers")

    items = [ item for item in self._config['loggers']
              if item.get("qualname") == qualname ]
    if len(items) == 0:
      raise AssertionError(f"{qualname} is not defined")
    elif len(items) > 1:
      raise AssertionError(f"{qualname} is defined multiple times")
    
    item  = items[0]

    logfile     = item.get("logfile")
    add_console = item.get("add_console")
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

    logger.setLevel(level)
    return logger
  
  @classmethod
  def map_level(cls, name : str):
    level = getattr(logging, name)
    return level


# if __name__ == '__main__':
#   factory = LoggerFactory()
#   factory.configure("conf/logger.yaml")

#   root = factory()
#   root.warning("from the root logger")

#   app = factory("app")
#   app.info("from the app logger")

#   bp = factory("app.base_params")
#   bp.debug("from the base_params logger")
