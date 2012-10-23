import verify

class Tree:
  def __init__(self, elements):
    self.elements = elements

  def count(self):
    return len(self.elements)

  def text(self):
    return self.elements[0]

def parse(stream):
  scanner = verify.Scanner(stream)
  command = verify.read_sexp(scanner)
  tokens = []
  if command != None:
    tokens += [command]
  return Tree(tokens)

