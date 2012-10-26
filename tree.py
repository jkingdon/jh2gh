import verify

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

def read_expression(scanner):
    while True:
        tok = scanner.get_tok()
        if tok == None:
            return None
        if tok == '(':
            result = []
            while 1:
                subsexp = read_expression(scanner)
                if subsexp == ')':
                    break
                elif subsexp == None:
                    raise SyntaxError('eof inside sexp')
                result.append(subsexp)
            return result
        else:
            return tok

def parse(stream):
  scanner = verify.Scanner(stream)
  tokens = []
  while True:
    expression = read_expression(scanner)
    if expression == None:
      break
    tokens += [expression]
  return Tree(tokens)

