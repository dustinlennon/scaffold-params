
import jinja2
from scaffold.params.base_mixin import BaseMixin

class JinjaTemplateMixin(BaseMixin):
  def assign_params(self, conf, args):
    super().assign_params(conf, args)
    self._j2env = jinja2.Environment(
      loader = jinja2.FileSystemLoader(str(args.template_path))
    )

  def get_template(self, name, parent = None, globals = None) -> jinja2.Template:
    return self._j2env.get_template(name, parent = parent, globals = globals)
