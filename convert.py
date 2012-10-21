import verify

class Convert:
  def convert(self, input):
    scanner = verify.Scanner(input)
    result = ""
    spacer = ""
    while True:
      command = verify.read_sexp(scanner)
      if command == None:
        break
      arguments = verify.read_sexp(scanner)

      if command == "kind" and arguments[0] == "variable":
        continue

      if command == "var":
        if arguments[0] == "variable":
          arguments[0] = "object"
        else:
          command = "tvar"

      result += spacer
      result += verify.sexp_to_string(command)
      result += " "
      result += verify.sexp_to_string(arguments)
      spacer = "\n"
    return result

