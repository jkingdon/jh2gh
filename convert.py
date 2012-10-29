import tokenizer
import tree

class Convert:
  def convert(self, input):
    expressions = tree.parse(input)
    i = 0
    while i < expressions.count():
      command_index = i
      argument_index = i + 1
      i += 2

      command = expressions[command_index]
      arguments = expressions[argument_index]

      if command == "kind" and arguments[0] == "variable":
        expressions[command_index] = '';
        expressions[argument_index] = '';
      elif command == "var":
        if arguments[0] == "variable":
          arguments[0] = "object"
        else:
          expressions[command_index] = "tvar"
    return expressions.to_string()

