from scaffold.params.logger_initializer import LoggerInitializer, logging
from scaffold.params.base_mixin import BaseMixin

class LoggerInitializerMixin(BaseMixin):
  def assign_params(self, conf, args):
    super().assign_params(conf, args)
    initializer = LoggerInitializer()
    initializer.configure(
      logs_path = str(args.logs_path),
      conf      = conf.logger
    )
    self._log_initializer = initializer

  def get_logger(self, qualname) -> logging.Logger:
    return logging.getLogger(qualname)
