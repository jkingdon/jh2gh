import tokenizer
import tree
import copy

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

