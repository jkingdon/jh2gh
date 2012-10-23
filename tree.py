import verify

class Tree:
  def __init__(self, elements):
    self._elements = elements

  def count(self):
    return len(self._elements)

  def elements(self):
    return self._elements

def parse(stream):
  scanner = verify.Scanner(stream)
  command = verify.read_sexp(scanner)
  tokens = []
  if command != None:
    tokens += [command]
  return Tree(tokens)

