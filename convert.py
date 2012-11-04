#encoding: utf-8
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
    self._terms = {}

  def store_variables(self, kind, variables):
    if not kind in self._variables:
      self._variables[kind] = []
    self._variables[kind] += variables

  def undo_pseudo_infix(self, expression):
    term_index = None
    for i in xrange(0, len(expression)):
      element = expression[i]
      if element in self._terms:
        term_index = i
      elif element.__class__ == tree.Tree:
        self.undo_pseudo_infix(element)
    if term_index != None:
      term = expression[term_index]
      for j in xrange(term_index):
        expression[j + 1] = expression[j]
      expression[0] = term

  def capitalize_term(self, term):
    if term == "∨":
      return "Disjunction"
    else:
      return term.capitalize()

  def equality_operator(self, kind):
    if kind == "formula":
      return "↔"
    else:
      return '='

  def convert(self, input):
    expressions = tree.parse(input)
    i = 0
    while i < len(expressions):
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
        name = name_and_arguments[0]

        self._terms[name] = return_type

        for j in xrange(1, len(name_and_arguments)):
          name_and_arguments[j] = assigner.next_name(name_and_arguments[j])
      elif command == "def":
        definiendum = arguments[0]
        definiens = copy.deepcopy(arguments[1])
        self.undo_pseudo_infix(definiens)
        defined_term = definiendum[0]
        term_type = self._terms[definiens[0]]

        expressions[i] = "term"
        expressions[i + 1] = tree.Tree(
          [term_type, ' ', copy.deepcopy(definiendum)])

#        expressions.insert(i + 2, "\n")
        expressions.insert(i + 2, "stmt")
        stmt_args = tree.Tree([
          self.capitalize_term(defined_term),
          tree.Tree([]),
          tree.Tree([]),
          tree.Tree([self.equality_operator(term_type),
            definiendum, definiens])
        ])
        expressions.insert(i + 3, stmt_args)

        i += 2

      self.undo_pseudo_infix(arguments)
      i += 2

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
  input = open(sys.argv[1], "r")
  output = open(sys.argv[2], "w")

  output.write(Wiki().convert(input))

