
from scaffold.params.logger_factory import LoggerFactory, logging
from .base_mixin import BaseMixin


class LoggerInitMixin(BaseMixin):
  def assign_args(self, args):
    super().assign_args(args)
    factory = LoggerFactory()
    factory.configure(str(args.logconf_path))
    self._factory = factory

  def get_logger(self, qualname) -> logging.Logger:
    return self._factory(qualname)
