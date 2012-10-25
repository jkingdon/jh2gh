class Tokenizer:
  def __init__(self, stream):
    self.stream = stream

  def read_all(self):
    tokens = []
    current_token = ''
    line = ''
    while True:
      if line == '':
        line = self.stream.readline()
        if line == '':
          break

      first = line[0]; line = line[1:]
      if first.isspace():
        if current_token.isspace() or current_token == '':
          current_token += first
        else:
          tokens += [current_token]; current_token = ''
          current_token += first
      elif first == '(' or first == ')':
        if current_token != '':
          tokens += [current_token]; current_token = ''
        current_token += first
      elif first == '#':
        if current_token != '':
          tokens += [current_token]; current_token = ''
        current_token = current_token + first + line
        line = ''
      else:
        if (current_token.isspace() or
            current_token == '(' or current_token == ')' or
            current_token[0:1] == '#'):
          tokens += [current_token]; current_token = ''
          current_token += first
        else:
          current_token += first

    if current_token != '':
      tokens += [current_token]
    return tokens

def tokenize(stream):
  return Tokenizer(stream).read_all()

