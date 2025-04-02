from scaffold.params.logger_factory import LoggerFactory, logging
from scaffold.params.base_mixin import BaseMixin

class LoggerInitMixin(BaseMixin):
  def assign_params(self, conf, args):
    super().assign_params(conf, args)
    factory = LoggerFactory()
    factory.configure(
      logs_path = str(args.logs_path),
      conf      = conf.logger
    )
    self._factory = factory

  def get_logger(self, qualname) -> logging.Logger:
    return self._factory(qualname)