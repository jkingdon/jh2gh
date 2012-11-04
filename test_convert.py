# encoding: utf-8

import unittest
import convert
import string_stream

class test_convert(unittest.TestCase):
  def process(self, inputString):
    return convert.Convert().convert(string_stream.StringStream(inputString))

  def test_empty(self):
    self.assertEqual("", self.process(""))

  def test_kind(self):
    self.assertEqual("kind (formula)", self.process("kind (formula)"))

  def test_should_preserve_whitespace_except_between_command_and_args(self):
    self.assertEqual("\t\nkind  \t\n(   formula \t )\n\n",
      self.process("\t\nkind  \t\n(   formula \t )\n\n"))

  def test_var_to_tvar(self):
    self.assertEqual("kind (formula)\ntvar (formula p)", self.process(
      "kind (formula)\nvar (formula p)"))

  def test_converts_var_to_var_for_kind_variable(self):
    # Might be kind of nice to clean up the whitespace where we remove
    # "kind (variable)", but maybe that isn't needed
    self.assertEqual("kind (object)\n \nvar (object x)", self.process(
      "kind (object)\nkind (variable)\nvar (variable x)"))

  def test_keeps_list_of_symbols_by_kind(self):
    converter =  convert.Convert()
    inputString = "var (formula p q)\nvar (formula r)\n"
    converter.convert(string_stream.StringStream(inputString))
    self.assertEqual({'formula': ['p', 'q', 'r']}, converter._variables)

  def test_can_assign_symbols_from_list(self):
    assigner = convert.VariableAssigner({'formula': ['p', 'q', 'r']})
    self.assertEqual('p', assigner.next_name('formula'))
    self.assertEqual('q', assigner.next_name('formula'))

  def test_converts_basic_stmt(self):
    result = self.process("""
kind (formula)
var (formula p q)
term (formula (→ formula formula))
stmt (AntecedentIntroduction () () (→ p (→ q p)))
""")
    self.assertEqual("""
kind (formula)
tvar (formula p q)
term (formula (→ p q))
stmt (AntecedentIntroduction () () (→ p (→ q p)))
""", result)

  def test_undoes_pseudo_infix(self):
    result = self.process("""
kind (formula)
var (formula p q)
term (formula (→ formula formula))
stmt (AntecedentIntroduction () () (p → (q → p)))
""")
    self.assertEqual("""
kind (formula)
tvar (formula p q)
term (formula (→ p q))
stmt (AntecedentIntroduction () () (→ p (→ q p)))
""", result)

  def test_undo_pseudo_infix_in_rule(self):
    result = self.process("""
kind (formula)
var (formula p q)
term (formula (→ formula formula))
stmt (applyModusPonens () (p (p → q)) q)
""")
    self.assertEqual("""
kind (formula)
tvar (formula p q)
term (formula (→ p q))
stmt (applyModusPonens () (p (→ p q)) q)
""", result)

  def test_turn_def_into_term_and_statement(self):
    result = self.process("""
kind (formula)
kind (number)
var (number x y)
term (formula (= number number))
term (number (double number))
def ((quadruple x) (double (double x)))
""")
    self.assertEqual("""
kind (formula)
kind (number)
tvar (number x y)
term (formula (= x y))
term (number (double x))
term (number (quadruple x))stmt(Quadruple()()(=(quadruple x)(double (double x))))
""", result)
    # This is the better spacing, when we can get the convert to be smarter about whitespace and insertion
#    self.assertEqual("""
#kind (formula)
#kind (number)
#tvar (number x y)
#term (formula (= x y))
#term (number (double x))
#term (number (quadruple x))
#stmt (Quadruple () () (= (quadruple x) (double (double x))))
#""", result)

  def test_convert_definition_of_predicate(self):
    result = self.process("""
kind (formula)
var (formula p q)
term (formula (→ formula formula))
term (formula (¬ formula))
def ((∨ p q) ((¬ p) → q))
""")
    self.assertEqual("""
kind (formula)
tvar (formula p q)
term (formula (→ p q))
term (formula (¬ p))
term (formula (∨ p q))stmt(Disjunction()()(↔(∨ p q)(→ (¬ p) q)))
""", result)

  def test_def_is_not_the_last_thing(self):
    result = self.process("""
kind (formula)
var (formula p q)
term (formula (¬ formula))
def ((double-not p) (¬ (¬ p)))
term (formula (→ formula formula))
""")
    self.assertEqual("""
kind (formula)
tvar (formula p q)
term (formula (¬ p))
term (formula (double-not p))stmt(Double-not()()(↔(double-not p)(¬ (¬ p))))
term (formula (→ p q))
""", result)

  def test_convert_def_which_relies_on_another_def(self):
    result = self.process("""
kind (formula)
var (formula p q)
term (formula (¬ formula))
def ((double-not p) (¬ (¬ p)))
def ((four-not p) (double-not (double-not p)))
""")
    self.assertEqual("""
kind (formula)
tvar (formula p q)
term (formula (¬ p))
term (formula (double-not p))stmt(Double-not()()(↔(double-not p)(¬ (¬ p))))
term (formula (four-not p))stmt(Four-not()()(↔(four-not p)(double-not (double-not p))))
""", result)

  def test_undoing_infix_and_defs_which_rely_on_others(self):
    result = self.process("""
kind (formula)
var (formula p q)
term (formula (¬ formula))
def ((double-not p) (¬ (¬ p)))
def ((four-not p) ((p double-not) double-not))
""")
    self.assertEqual("""
kind (formula)
tvar (formula p q)
term (formula (¬ p))
term (formula (double-not p))stmt(Double-not()()(↔(double-not p)(¬ (¬ p))))
term (formula (four-not p))stmt(Four-not()()(↔(four-not p)(double-not (double-not p))))
""", result)

  def wiki(self, string):
    return convert.Wiki().read(string_stream.StringStream(string))

  def wiki_convert(self, string):
    return convert.Wiki().convert(string_stream.StringStream(string))

  def test_read_wiki_no_proof(self):
    self.assertEqual("", self.wiki("I\nam a proof\nsite\n"))

  def test_read_wiki_open_jh(self):
    input = "<jh>\nkind (formula)\n</jh>\n"
    self.assertEqual("kind (formula)\n", self.wiki(input))

  def test_read_wiki_multiple_jh(self):
    input = "<jh>\nkind\n</jh>\nhere we define it\n<jh>\n (formula)\n</jh>\n"
    self.assertEqual("kind\n (formula)\n", self.wiki(input))

  def test_converts_proofs_in_wiki(self):
    self.assertEqual("kind (formula)\ntvar (formula p)\n", self.wiki_convert(
      "<jh>\nkind (formula)\nvar (formula p)\n</jh>\n"))

