class StringStream:
     def __init__(self, s):
          self.lines = s.split('\n')
          self.ix = 0
     def readline(self):
          if self.ix >= len(self.lines):
               return ''
          elif self.ix == len(self.lines) - 1:
               result = self.lines[self.ix]
               self.ix += 1
               return result
          else:
               result = self.lines[self.ix] + '\n'
               self.ix += 1
               return result

class OutputStream:
  def __init__(self):
    self._contents = ""
  def write(self, data):
    self._contents += data
  def contents(self):
    return self._contents

class Opener:
  def __init__(self):
    self._files = {}

  def set_file(self, name, stream):
    self._files[name] = stream

  def open_file(self, name):
    if self._files.has_key(name):
      return self._files[name]
    else:
      raise Exception("No such (fake) file " + name)

