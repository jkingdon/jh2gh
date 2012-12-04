class WikiTokenizer:
  def __init__(self, stream):
    self._stream = stream
    self._in_proof = False

  def read_line_or_wiki_token(self):
    while True:
      line = self._stream.readline()
      if line == '':
        return line
      elif line == "<jh>\n":
        self._in_proof = True
      elif line == "</jh>\n":
        self._in_proof = False
      elif self._in_proof:
        return line
      else:
        return Wiki(line)

class GhilbertTokenizer:
  def __init__(self, stream):
    self._stream = stream

  def read_line_or_wiki_token(self):
    return self._stream.readline()

class Tokenizer:
  def __init__(self, stream):
    self._wiki_tokenizer = GhilbertTokenizer(stream)
    self.line = ''

  def next_token(self):
    current_token = ''
    while True:
      if self.line == '':
        line_or_wiki_token = self._wiki_tokenizer.read_line_or_wiki_token()
        if line_or_wiki_token == '':
          break
        if line_or_wiki_token.__class__ == Wiki:
          return line_or_wiki_token
        self.line = line_or_wiki_token

      first = self.line[0]
      if first.isspace():
        if current_token.isspace() or current_token == '':
          current_token += first
        else:
          return current_token
      elif first == '(' or first == ')':
        if current_token != '':
          return current_token
        current_token += first
      elif first == '#':
        if current_token != '':
          return current_token
        token = self.line
        self.line = ''
        return token
      else:
        if (current_token.isspace() or
            current_token == '(' or current_token == ')' or
            current_token[0:1] == '#'):
          return current_token
        else:
          current_token += first
      self.line = self.line[1:]

    if current_token != '':
      return current_token
    return None

  def read_all(self):
    tokens = []
    while True:
      token = self.next_token()
      if token == None:
        break
      tokens += [token]
    return tokens

def tokenize(stream):
  return Tokenizer(stream).read_all()

class Wiki:
  def __init__(self, text):
    pass

