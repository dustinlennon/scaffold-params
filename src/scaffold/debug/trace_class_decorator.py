import types
import functools
import textwrap

from scaffold.debug import _printf_debug, ansi_color_codes as color
 
class TraceClassDecorator(object):
  _indent = 0

  def __init__(self, include = None, exclude = None, mro = False):
    self._include = include
    self._exclude = exclude
    self._mro     = mro

  def _omit_class(self, cls):
    if cls.__name__.startswith("_"):
      return True
    elif cls is object:
      return True
    else:
      return False

  def _get_class_set(self, cls):
    if self._mro:
      classes = cls.__mro__
    else:
      classes = [ cls ]

    classes = [ K for K in classes if not self._omit_class(K) ]

    return classes

  @classmethod
  def _debug_call(cls, owner, qual_name, *args, **kw):

    # In certain edge cases, repr can generate RecursionError; 
    # c.f., ExceptionThrowingParser
    zargs = []
    for a in args:
      if type(a) is owner:
        zargs.append(object.__repr__(a))
      else:
        zargs.append(repr(a))
    args_s = ", ".join(zargs)

    zkw = {}
    for k,v in kw.items():
      if type(v) is owner:
        zkw[k] = object.__repr__(v)
      else:
        zkw[k] = repr(v)
    kw_s = ", ".join([f"{k}={v}" for k,v in zkw.items()])

    s = ",".join(
      [item for item in (args_s, kw_s) if item != ""]
    )

    indent = '.' * (cls._indent - 2)
    msg = textwrap.fill(
      color.BLUE + color.BOLD + f"{qual_name}" + color.END + "(" + color.GREY + s + color.END + ")",
      width = 132,
      initial_indent = indent,
      subsequent_indent = indent
    )
    _printf_debug(msg, prefix='') 

  @classmethod
  def _wrap_call(cls, owner, fn, *args, **kw):
    cls._indent = cls._indent + 2
    cls._debug_call(owner, fn.__qualname__, *args, **kw)

    try:
      val = fn(*args, **kw)
    finally:
      cls._indent = cls._indent - 2
    return val

  def wrapper(self, cls, fn):
    @functools.wraps(fn)
    def wfn(*args, **kw):
      return TraceClassDecorator._wrap_call(cls, fn, *args, **kw)
    
    setattr(wfn, "__scaffold_wrapped", None)
    return wfn

  def wrap(self, cls, attr_name):
    attr = cls.__dict__.get(attr_name)

    if hasattr(attr, '__scaffold_wrapped'):
      return

    if isinstance(attr, types.FunctionType):
      wrapped = self.wrapper(cls, attr)
      setattr(cls, attr_name, wrapped)

    elif isinstance(attr, classmethod):
      wrapped = self.wrapper(cls, attr.__func__)
      setattr(cls, attr_name, classmethod(wrapped))

    elif isinstance(attr, staticmethod):
      wrapped = self.wrapper(cls, attr.__func__)
      setattr(cls, attr_name, staticmethod(wrapped))


  def __call__(self, cls):
    class_set = self._get_class_set(cls)
    for K in class_set:
      attrs = K.__dict__.keys()

      for attr_name in attrs:        
        if self._include:
          if attr_name not in self._include:
            continue

        if self._exclude:
          if attr_name in self._exclude:
            continue

        self.wrap(K, attr_name)

    return cls


if __name__ == '__main__':

  class A:
    cvar = None

    def __init__(self):
      """
      Some documentation for A.__init__
      """
      pass

    def foo(self, v : int):
      """
      Some documentation for A.foo
      """
      pass

    @classmethod
    def bar(cls):
      pass

    @staticmethod
    def baz():
      pass

  @TraceClassDecorator(mro = True)
  class B(A):
    def __init__(self):
      """
      Some documentation for B.__init__
      """
      super().__init__()

    def foo(self, v : int):
      """
      Some documentation for B.foo
      """
      super().foo(v)
      

  A.bar()
  A.baz()
  a = A()

  cm = A.__dict__['bar']
  im = A.__dict__['foo']
  sm = A.__dict__['baz']

  b = B()
  b.foo(0)

  B.baz()

