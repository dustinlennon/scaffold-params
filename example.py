"""
A sample run with multiple timezone overrides

KEYSERVER_TIMEZONE=UTC \
PRINTF_DEBUG=True \
python3 example.py \
  --timezone US/Eastern
"""

from scaffold.base_params import BaseParams
from scaffold.mixins import *

if __name__ == '__main__':

  class CommonParams(NowMixin, LoggerInitMixin, JinjaTemplateMixin):
    pass

  class ExampleParams(BaseParams, CommonParams):
    _prefix = "EXAMPLE"

  params = ExampleParams.build()
  args = params.parse_args()

  # NowMixin provides params.now()
  msg = f"The time is: {params.now().strftime("%H:%M %Z")}"

  # LoggerInitMixin provides 'params.get_logger'
  logger = params.get_logger(__name__)
  logger.info(msg)

  # JinjaTemplateMixin provides 'params.get_template'
  template = params.get_template("example.j2")
  content = template.render(
    msg = msg
  )
  print(content)
