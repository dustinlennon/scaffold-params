import argparse

class ParserFallbackException(Exception):
  def __init__(self, *args, parser, **kwargs):
    super().__init__(*args, **kwargs)
    self.parser = parser

class ExceptionThrowingParser(argparse.ArgumentParser):
  def __init__(self, *args, add_help = False, exit_on_error = False, **kw):
    super().__init__(
      *args,
      add_help = add_help,
      exit_on_error = exit_on_error,
      **kw
    )

  def exit(self, status = 0, message = None):
    if status:
      raise ParserFallbackException(message, parser = self)
    
  def _err_msg(self, message):
    args = {'prog': self.prog, 'message': message}
    return ('%(prog)s: error: %(message)s\n') % args

  def error(self, message):
    self.exit(2, self._err_msg(message))
