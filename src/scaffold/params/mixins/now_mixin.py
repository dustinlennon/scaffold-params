import datetime, pytz
from scaffold.params.base_mixin import BaseMixin

class NowMixin(BaseMixin):
  def assign_params(self, conf, args):
    super().assign_params(conf, args)
    self.timezone = args.timezone

  def now(self) -> datetime:
    self._tz  = pytz.timezone(self.timezone)
    return datetime.datetime.now(self._tz)
