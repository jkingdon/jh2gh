class StringStream:
     def __init__(self, s):
          self.lines = s.split('\n')
          self.ix = 0
     def readline(self):
          if self.ix >= len(self.lines):
               return ''
          else:
               result = self.lines[self.ix] + '\n'
               self.ix += 1
               return result


