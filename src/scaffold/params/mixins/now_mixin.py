import datetime, pytz
from scaffold.params.base_mixin import BaseMixin
from scaffold.params import _printf_debug

class NowMixin(BaseMixin):
  def assign_args(self, args):
    _printf_debug("NowMixin.assign_args")
    super().assign_args(args)
    self.timezone = args.timezone

  def now(self) -> datetime:
    self._tz  = pytz.timezone(self.timezone)
    return datetime.datetime.now(self._tz)
