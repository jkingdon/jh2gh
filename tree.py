import verify
import tokenizer

class Tree:
  def __init__(self, elements):
    self._elements = elements

  def count(self):
    return len(self._elements)

  def elements(self):
    result = []
    for element in self._elements:
      if element.__class__ == Tree:
        result += [element.elements()]
      else:
        result += [element]
    return result

  def to_string(self):
#    return ' '.join( list comprehension blah blah blah
    with_parentheses = verify.sexp_to_string(self._elements)
    return with_parentheses[1:(len(with_parentheses)-1)]

def read_expression(tokenizer1):
    while True:
        token = tokenizer1.next_token()
        if token == None:
            return None
        if token.isspace() or token.startswith("#"):
            continue
        if token == '(':
            result = []
            while True:
                subsexp = read_expression(tokenizer1)
                if subsexp == ')':
                    break
                elif subsexp == None:
                    raise SyntaxError('eof inside sexp')
                result.append(subsexp)
            return result
        else:
            return token

def parse(stream):
  tokenizer1 = tokenizer.Tokenizer(stream)
  tokens = []
  while True:
    expression = read_expression(tokenizer1)
    if expression == None:
      break
    tokens += [expression]
  return Tree(tokens)

