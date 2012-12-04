import tokenizer

class Tree:
  def __init__(self, elements):
    self._elements = elements

  def __len__(self):
    return len(self.elements_children_as_trees())

  def is_semantic(self, element):
    if element.__class__ == Tree:
      return True
    elif element.__class__ == tokenizer.Wiki:
      return False
    elif element.__class__ == 'foo'.__class__:
      return not element.isspace() and not element.startswith("#")
    else:
      raise Exception("don't know what to do with " + element.__class__.__name__)

  def elements_children_as_trees(self):
    return [element for element in self._elements if self.is_semantic(element)]

  def elements_including_whitespace(self):
    return [element for element in self._elements if element.__class__ != tokenizer.Wiki]

  def raw_index(self, cooked_index):
    cooked = 0
    for raw in xrange(len(self._elements)):
      if cooked == cooked_index:
        return raw
      element = self._elements[raw]
      if (element.__class__ == Tree or
        (not element.isspace() and not element.startswith("#"))):
        cooked += 1
    return len(self._elements)

  def insert(self, index, new_elements):
    raw_index = self.raw_index(index)
    self._elements[raw_index:raw_index] = new_elements

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

  def __repr__(self):
    result = ''
    for element in self._elements:
      if element.__class__ == Tree:
        result += '('
        result += repr(element)
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
  return parse_from_tokenizer(tokenizer.Tokenizer(stream))

def parse_from_tokenizer(tokenizer1):
  expressions = []
  while True:
    expression = read_expression(tokenizer1)
    if expression == None:
      break
    expressions.append(expression)
  return Tree(expressions)

