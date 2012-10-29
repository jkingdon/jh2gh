import tokenizer
import tree

class Convert:
  def convert(self, input):
    result = ""
    spacer = ""
    expressions = tree.parse(input)
    i = 0
    while i < expressions.count():
      command = expressions[i]
      arguments = expressions[i + 1]
      i += 2

      if command == "kind" and arguments[0] == "variable":
        continue

      if command == "var":
        if arguments[0] == "variable":
          arguments[0] = "object"
        else:
          command = "tvar"

      result += spacer
      result += command
      result += " ("
      result += arguments.to_string()
      result += ")"
      spacer = "\n"
    return result

