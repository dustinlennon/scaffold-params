
import jinja2
from .base_mixin import BaseMixin

class JinjaTemplateMixin(BaseMixin):
  def assign_args(self, args):
    # _printf_debug(f"JinjaTemplateMixin.assign_args()")
    super().assign_args(args)
    self._j2env = jinja2.Environment(
      loader = jinja2.FileSystemLoader(args.template_path)
    )

  def get_template(self, name, parent = None, globals = None) -> jinja2.Template:
    return self._j2env.get_template(name, parent = parent, globals = globals)
