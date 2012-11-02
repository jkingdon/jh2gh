import tokenizer

class Tree:
  def __init__(self, elements):
    self._elements = elements

  def count(self):
    return len(self.elements())

  def __len__(self):
    return len(self.elements())

  def elements(self):
    return [element.elements() if element.__class__ == Tree else element
      for element in self.elements_children_as_trees()]

  def elements_children_as_trees(self):
    return [element for element in self._elements
      if element.__class__ == Tree or
        (not element.isspace() and not element.startswith("#"))
      ]

  def __getitem__(self, index):
    return self.elements_children_as_trees()[index]

  def __setitem__(self, index, value):
    non_whitespace = -1
    j = 0
    while j < len(self._elements):
      element = self._elements[j]
      if element.__class__ == Tree:
        non_whitespace += 1
      elif element.isspace() or element.startswith("#"):
        j += 1
        continue
      else:
        non_whitespace += 1
      if non_whitespace == index:
        self._elements[j] = value
        return
      j += 1

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

