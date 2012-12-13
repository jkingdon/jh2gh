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
    if not kind in self._variables:
      raise Exception("Need variables for kind " + kind)
    elif len(self._variables[kind]) == 0:
      raise Exception("Ran out of variables for kind " + kind)
    else:
      return self._variables[kind].pop(0)

class FileOpener:
  def open_file(self, name):
    return open(name)

class Convert:
  def __init__(self, proof_filename = None):
    self._variables = {}
    self._terms = {}
    self._opener = FileOpener()
    self._proof_filename = proof_filename

  def store_variables(self, kind, variables):
    if not kind in self._variables:
      self._variables[kind] = []
    self._variables[kind] += variables

  def undo_pseudo_infix(self, expression):
    if expression.__class__ != tree.Tree:
      raise Exception("expected tree, got " + str(expression))

    term_index = None
    for i in range(0, len(expression)):
      element = expression[i]
      if element in self._terms:
        term_index = i
      elif element.__class__ == tree.Tree:
        self.undo_pseudo_infix(element)
    if term_index != None:
      term = expression[term_index]
      for j in range(term_index - 1, -1, -1):
        expression[j + 1] = expression[j]
      expression[0] = term

  def capitalize_term(self, term):
    preset_names = {
      '∨': 'Disjunction',
      '∧': 'Conjunction',
      '↔': 'Biconditional',
      '→': 'Implication',
      '¬': 'Negation'
    }
    if term in preset_names:
      return preset_names[term]
    else:
      return term.capitalize()

  def term_kind(self, definiens):
    if definiens[0].__class__ == 'a'.__class__:
      return self._terms[definiens[0]]
    else:
      raise Exception("Cannot figure out kind of " + str(definiens))

  def equality_operator(self, kind):
    if kind == "formula" or kind == "wff":
      return "↔"
    else:
      return '='

  def convert(self, input):
    expressions = tree.parse(input)
#    try:
    self.convert_tree(expressions)
#    except:
#      print "Got an exception"
#      print repr(expressions)
    return repr(expressions)

  def convert_tree(self, expressions):
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
      elif command == "import" or command == "export":
        self.process_import_or_export(command, arguments)
      elif command == "term":
        assigner = VariableAssigner(self._variables)
        return_type = arguments[0]
        name_and_arguments = arguments[1]
        name = name_and_arguments[0]

        self._terms[name] = return_type

        for j in range(1, len(name_and_arguments)):
          name_and_arguments[j] = assigner.next_name(name_and_arguments[j])
      elif command == "def":
        definiendum = arguments[0]
        definiens = copy.deepcopy(arguments[1])
        self.undo_pseudo_infix(definiens)
        defined_term = definiendum[0]
        term_type = self.term_kind(definiens)

        expressions[i] = "term"
        expressions[i + 1] = tree.Tree(
          [term_type, ' ', copy.deepcopy(definiendum)])
        self._terms[definiendum[0]] = term_type

        if not (defined_term in ["→", "∧", "↔"]):
          stmt_args = tree.Tree([
            self.capitalize_term(defined_term),
            " ",
            tree.Tree([]),
            " ",
            tree.Tree([]),
            " ",
            tree.Tree([
              self.equality_operator(term_type),
              " ",
              definiendum,
              " ",
              definiens])
          ])
          expressions.insert(i + 2, ["\n", "stmt", " ", stmt_args])

          i += 2
      elif command == "thm":
        name = arguments[0]
        distinctness_constraints = arguments[1]
        hypotheses = arguments[2]
        conclusion = arguments[3]
        proof = arguments[4]

        arguments[4] = ''
        arguments.insert(4, proof.all_elements())

        new_hypotheses = []
        first_time = True
        for h in hypotheses:
          hypothesis_name = h[0]
          expression = h[1]
          if not first_time:
            new_hypotheses.append(" ")
          new_hypotheses.append(hypothesis_name)
          new_hypotheses.append(" ")
          new_hypotheses.append(expression)
        arguments[2] = tree.Tree(new_hypotheses)

        if self._proof_filename != None:
          wiki = "* "

          if len(hypotheses) > 0:
            prefix = ""
            for h in hypotheses:
              expression = h[1]
              wiki += prefix + "#(" + repr(expression) + ")#"
              prefix = ", "
            wiki += " ⊢ "

          wiki += ("#(" + repr(conclusion) + ")#" +
            " ([" + self._proof_filename + "/" + name + " | " + name + "])\n")

          # Insert between 'thm' and arguments, to handle wikitext before/after thm
          expressions.insert(i + 1, [tokenizer.Wiki(wiki)])
          i += 1

      self.undo_pseudo_infix(arguments)
      i += 2

  def set_opener(self, opener):
    self._opener = opener

  def process_import_or_export(self, command, arguments):
    name = arguments[0]
    underscored_name = arguments[1]
    params = arguments[2]
    prefix = arguments[3]

    if prefix.__class__ == tree.Tree and len(prefix) == 0:
      arguments[3] = '""'
    arguments[1] = self.ghilbert_filename(underscored_name)

    if command == "import":
      filesystem_name = self.convert_filename(underscored_name)
      stream = self._opener.open_file(filesystem_name)
      self.convert(tokenizer.WikiTokenizer(stream))

  def convert_filename(self, underscored_name):
    namespace, name = self.split_filename(underscored_name)
    name = name.replace("_", " ")
    return (namespace + "/" + name[0] + "/" + name[1] + "/" +
      name[2] + "/" + name)

  def ghilbert_filename(self, underscored_name):
    namespace, name = self.split_filename(underscored_name)
    if namespace == 'Main':
      suffix = ".gh"
    elif namespace == 'Interface':
      suffix = ".ghi"
    else:
      raise Exception("Don't know how to convert namespace " + namespace)
    return name + suffix;

  def split_filename(self, underscored_name):
    components = underscored_name.split(":")
    if len(components) == 1:
      namespace = "Main"
      name = underscored_name
    else:
      namespace, name = components

    return [namespace, name]

class Wiki:
  def __init__(self, input, proof_filename, wiki_out):
    self._tree = tree.parse(tokenizer.WikiTokenizer(input))
    self._proof_filename = proof_filename
    self._wiki_out = wiki_out
    self._proof = ''

  def to_string_wiki_to_wiki_out(self):
    for element in self._tree.all_elements():
      if element.__class__ == tree.Tree:
        self._proof += '('
        self._proof += element.to_string_wiki_to_comment()
        self._proof += ')'
      elif element.__class__ == tokenizer.Wiki:
        self._wiki_out.write(element.text())
      else:
        self._proof += element

  def convert(self):
    Convert(self._proof_filename).convert_tree(self._tree)
    self.to_string_wiki_to_wiki_out()
    return self._proof

if __name__ == '__main__':
  if len(sys.argv) != 2:
    sys.stderr.write('Usage: python convert.py UNDERSCORED-NAME\n')
    sys.stderr.write('  Run it from the wikiproofs directory.\n')
    sys.stderr.write('  It will output to ../ghilbert-app/general\n')
    sys.stderr.write('  UNDERSCORED-NAME is the name as specified in wikiproofs, e.g. Interface:Set_theory\n')
    exit(1)
  underscored_name = sys.argv[1]
  input = open(Convert().convert_filename(underscored_name), "r")
  proof_filename = "/general/" + Convert().ghilbert_filename(underscored_name)
  output = open("../ghilbert-app" + proof_filename, "w")
  output.write("# Creative Commons Attribution-Share Alike 3.0 Unported (http://creativecommons.org/licenses/by-sa/3.0/)\n")

  if underscored_name.split(":")[0] == "Interface":
    expressions = tree.parse(tokenizer.WikiTokenizer(input))
    Convert().convert_tree(expressions)
    output.write(expressions.to_string_wiki_to_comment())
  else:
    wiki_out = open("../ghilbert-app/wiki/general/" + underscored_name + ".ghm", "w")
    output.write(Wiki(input, proof_filename, wiki_out).convert())

