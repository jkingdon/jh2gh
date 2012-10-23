import verify

class Tree:
  def __init__(self, elements):
    self._elements = elements

  def count(self):
    return len(self._elements)

  def elements(self):
    return self._elements

  def to_string(self):
#    return ' '.join( list comprehension blah blah blah
    with_parentheses = verify.sexp_to_string(self._elements)
    return with_parentheses[1:(len(with_parentheses)-1)]

def parse(stream):
  scanner = verify.Scanner(stream)
  tokens = []
  while True:
    expression = verify.read_sexp(scanner)
    if expression == None:
      break
    tokens += [expression]
  return Tree(tokens)

