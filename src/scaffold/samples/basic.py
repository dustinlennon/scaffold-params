"""
A sample run with multiple timezone overrides

KEYSERVER_TIMEZONE=UTC \
PRINTF_DEBUG=True \
python3 samples/basic.py \
  --timezone US/Eastern
"""

from scaffold.params.base_params import BaseParams
from scaffold.params.mixins import *

if __name__ == '__main__':

  class CommonParams(NowMixin, LoggerInitMixin, JinjaTemplateMixin):
    pass

  class BasicParams(BaseParams, CommonParams):
    _prefix = "BASIC"

  params = BasicParams.build()
  args = params.parse_args()

  # NowMixin provides params.now()
  msg = f"The time is: {params.now().strftime("%H:%M %Z")}"

  # LoggerInitMixin provides 'params.get_logger'
  logger = params.get_logger(__name__)
  logger.info(msg)

  # JinjaTemplateMixin provides 'params.get_template'
  template = params.get_template("basic.j2")
  content = template.render(
    msg = msg
  )
  print(content)
