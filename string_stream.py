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


