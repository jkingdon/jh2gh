import sys

import tokenizer
import tree
import copy
import string_stream

class VariableAssigner:
  def __init__(self, variables):
    self._variables = copy.deepcopy(variables)

  def next_name(self, kind):
    return self._variables[kind].pop(0)

class Convert:
  def __init__(self):
    self._variables = {}

  def store_variables(self, kind, variables):
    if not self._variables.has_key(kind):
      self._variables[kind] = []
    self._variables[kind] += variables

  def convert(self, input):
    expressions = tree.parse(input)
    for i in xrange(0, len(expressions), 2):
      command = expressions[i]
      arguments = expressions[i + 1]

      if command == "kind" and arguments[0] == "variable":
        expressions[i] = '';
        expressions[i + 1] = '';
      elif command == "var":
        if arguments[0] == "variable":
          arguments[0] = "object"
        else:
          expressions[i] = "tvar"
        self.store_variables(arguments[0], arguments[1:])
      elif command == "term":
        assigner = VariableAssigner(self._variables)
        return_type = arguments[0]
        name_and_arguments = arguments[1]
        for i in xrange(1, len(name_and_arguments)):
          name_and_arguments[i] = assigner.next_name(name_and_arguments[i])

    return expressions.to_string()

class Wiki:
  def read(self, input):
    result = ''
    in_proof = False
    while True:
      line = input.readline()
      if line == '':
        break
      if line == "</jh>\n":
        in_proof = False
      elif in_proof:
        result += line

      if line == "<jh>\n":
        in_proof = True
    return result

  def convert(self, input):
    jhilbert = self.read(input)
    return Convert().convert(string_stream.StringStream(jhilbert))

if __name__ == '__main__':
  if len(sys.argv) != 3:
    print >> sys.stderr, 'Usage: JHILBERT-INPUT GHILBERT-OUTPUT'
    exit(1)
  input = sys.argv[1]
  output = sys.argv[2]

  result = Wiki().convert(open(input, "r"))
  print result

