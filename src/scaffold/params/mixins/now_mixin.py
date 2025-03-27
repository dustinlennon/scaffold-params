import datetime, pytz
from .base_mixin import BaseMixin

class NowMixin(BaseMixin):
  def assign_args(self, args):
    super().assign_args(args)
    self.timezone = args.timezone

  def now(self) -> datetime:
    self._tz  = pytz.timezone(self.timezone)
    return datetime.datetime.now(self._tz)
