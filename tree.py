import tokenizer

class Tree:
  def __init__(self, elements):
    self._elements = elements

  def count(self):
    return len(self.elements())

  def elements(self):
    result = []
    for element in self._elements:
      if element.__class__ == Tree:
        result += [element.elements()]
      elif element.isspace() or element.startswith("#"):
        continue
      else:
        result += [element]
    return result

  def to_string(self):
    result = ''
    for element in self._elements:
      if element.__class__ == Tree:
        result += '('
        result += element.to_string()
        result += ')'
      else:
        result += element
    return result

def read_expression(tokenizer1):
    while True:
        token = tokenizer1.next_token()
        if token == None:
            return None
        if token == '(':
            result = []
            while True:
                subsexp = read_expression(tokenizer1)
                if subsexp == ')':
                    break
                elif subsexp == None:
                    raise SyntaxError('eof inside sexp')
                result.append(subsexp)
            return Tree(result)
        else:
            return token

def parse(stream):
  tokenizer1 = tokenizer.Tokenizer(stream)
  expressions = []
  while True:
    expression = read_expression(tokenizer1)
    if expression == None:
      break
    expressions.append(expression)
  return Tree(expressions)

