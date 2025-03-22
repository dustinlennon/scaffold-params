import re
import os

class DotenvReader(object):
  def __init__(self, locs):
    self.locs = locs

  def read(self) -> dict:
    result = None
    for pth in self.locs:
      try:
        result = self.read_dotenv(pth)
      except FileNotFoundError:
        pass
      except TypeError:
        pass
      else:
        break

    if result is None:
      raise FileNotFoundError("no dotenv file found")
    
    return result

  @classmethod
  def read_dotenv(cls, pth):
    regex = re.compile(r"\${(?P<name>.*?)}")

    result = {}
    with open(pth) as f:
      for line in f.readlines():
        line = line.strip()
        if line == "" or line[0] == '#':
          continue        

        name, value = line.strip().split('=',1)                
        matches = list(regex.finditer(value))

        r = value
        for m in matches[::-1]:
          r = r[0:m.start()] + os.environ.get(m['name']) + r[m.end():]

        result[name] = r

    return result


