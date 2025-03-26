# import datetime, pytz
# import logging
# import jinja2

# from app import _printf_debug
# from app.logger_factory import LoggerFactory

class BaseMixin(object):
  def assign_args(self, args):
    # _printf_debug(f"ParamsMixin.assign_args()")
    pass

# class JinjaTemplateMixin(ParamsMixin):
#   def assign_args(self, args):
#     # _printf_debug(f"JinjaTemplateMixin.assign_args()")
#     super().assign_args(args)
#     self._j2env = jinja2.Environment(
#       loader = jinja2.FileSystemLoader(args.template_path)
#     )

#   def get_template(self, name, parent = None, globals = None) -> jinja2.Template:
#     return self._j2env.get_template(name, parent = parent, globals = globals)
 
# class LoggerInitMixin(ParamsMixin):
#   def assign_args(self, args):
#     # _printf_debug(f"LoggerInitMixin.assign_args()")
#     super().assign_args(args)
#     factory = LoggerFactory()
#     factory.configure(args.logconf_path)
#     self._factory = factory

#   def get_logger(self, qualname) -> logging.Logger:
#     return self._factory(qualname)

# class NowMixin(ParamsMixin):
#   def assign_args(self, args):
#     # _printf_debug(f"NowMixin.assign_args()")
#     super().assign_args(args)
#     self.timezone = args.timezone

#   def now(self) -> datetime:
#     self._tz  = pytz.timezone(self.timezone)
#     return datetime.datetime.now(self._tz)
