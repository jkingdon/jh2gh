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

  def test_undo_pseudo_infix_with_two_preceding_terms(self):
    result = self.process("""
kind (foo)
var (foo p q r s)
term (foo (≡ foo foo foo foo))
stmt (sss () (p q ≡ r s) (q p ≡ s r))
""")
    self.assertEqual("""
kind (foo)
tvar (foo p q r s)
term (foo (≡ p q r s))
stmt (sss () (≡ p q r s) (≡ q p s r))
""", result)

  def test_undo_pseudo_infix_and_whitespace(self):
    # exactly what happens to the whitespace might be corner-casey, but
    # we at least want things not to blow up and not eat comments (if there are any)
    result = self.process("""
kind (formula)
var (formula p q)
term (formula (→ formula formula))
stmt (AntecedentIntroduction () () (#beforep
p #afterp
→ #afterarrow
( #afterparen
q #afterq
→ #afternestedarrow
p #afternestedp
)))
""")
    self.assertEqual("""
kind (formula)
tvar (formula p q)
term (formula (→ p q))
stmt (AntecedentIntroduction () () (#beforep
→ #afterp
p #afterarrow
( #afterparen
→ #afterq
q #afternestedarrow
p #afternestedp
)))
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
term (number (quadruple x))
stmt (Quadruple () () (= (quadruple x) (double (double x))))
""", result)

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
term (formula (∨ p q))
stmt (Disjunction () () (↔ (∨ p q) (→ (¬ p) q)))
""", result)

  def test_handles_wff_like_formula(self):
    result = self.process("""
kind (wff)
var (wff p q)
term (wff (¬ wff))
def ((single-not p) (¬ p))
""")
    self.assertEqual("""
kind (wff)
tvar (wff p q)
term (wff (¬ p))
term (wff (single-not p))
stmt (Single-not () () (↔ (single-not p) (¬ p)))
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
term (formula (double-not p))
stmt (Double-not () () (↔ (double-not p) (¬ (¬ p))))
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
term (formula (double-not p))
stmt (Double-not () () (↔ (double-not p) (¬ (¬ p))))
term (formula (four-not p))
stmt (Four-not () () (↔ (four-not p) (double-not (double-not p))))
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
term (formula (double-not p))
stmt (Double-not () () (↔ (double-not p) (¬ (¬ p))))
term (formula (four-not p))
stmt (Four-not () () (↔ (four-not p) (double-not (double-not p))))
""", result)

  def test_propositional_logic_is_special_omit_defs_for_now(self):
    # The question here is how Principia handles definitions,
    # and how we can translate that (hopefully without having to
    # change it hugely). For now, we kind of punt.
    result = self.process("""
kind (formula)
var (formula p q)
term (formula (¬ formula))
term (formula (∨ formula formula))
def ((→ p q) ((¬ p) ∨ q))
def ((∧ p q) (¬ ((¬ p) ∨ (¬ q))))
def ((↔ p q) ((p → q) ∧ (q → p)))
""")
    self.assertEqual("""
kind (formula)
tvar (formula p q)
term (formula (¬ p))
term (formula (∨ p q))
term (formula (→ p q))
term (formula (∧ p q))
term (formula (↔ p q))
""", result)

  def wiki_convert(self, string):
    return convert.Wiki(string_stream.StringStream(string), "", string_stream.OutputStream()).convert()

  def test_read_wiki_no_proof(self):
    self.assertEqual("", self.wiki_convert("I\nam a proof\nsite\n"))

  def test_read_wiki_open_jh(self):
    input = "<jh>\nkind (formula)\n</jh>\n"
    self.assertEqual("kind (formula)\n", self.wiki_convert(input))

  def test_read_wiki_multiple_jh(self):
    input = "<jh>\nkind\n</jh>\nhere we define it\n<jh>\n (formula)\n</jh>\n"
    self.assertEqual("kind\n (formula)\n", self.wiki_convert(input))

  def test_converts_proofs_in_wiki(self):
    self.assertEqual("kind (formula)\ntvar (formula p)\n", self.wiki_convert(
      "<jh>\nkind (formula)\nvar (formula p)\n</jh>\n"))

  def test_writes_wiki_output(self):
    string = """Start of file.
<jh>
kind (formula)
</jh>
End of file.
"""
    out = string_stream.OutputStream()
    convert.Wiki(string_stream.StringStream(string), "", out).convert()
    self.assertEqual("Start of file.\nEnd of file.\n", out.contents())

  def test_wiki_text_in_a_proof_turn_to_comments(self):
    string = """<jh>
thm (foo () () () (
</jh>
Here we prove a theorem.
<jh>
  proof here
))
</jh>
"""
    out = string_stream.OutputStream()
    ghilbert = convert.Wiki(string_stream.StringStream(string), "file.gh", out).convert()
    self.assertEqual("* #()# ([file.gh/foo | foo])\n", out.contents())
    self.assertEqual("""thm (foo () () ()
# Here we prove a theorem.
  proof here
 )
""", ghilbert)

  def test_wiki_text_after_proof_goes_to_wiki(self):
    string = """<jh>
thm (foo () () () (
  proof here
))
</jh>
Here is some wikitext.
"""
    out = string_stream.OutputStream()
    ghilbert = convert.Wiki(string_stream.StringStream(string), "file.gh", out).convert()
    self.assertEqual("* #()# ([file.gh/foo | foo])\nHere is some wikitext.\n", out.contents())

  def test_add_references_to_theorems_to_wiki(self):
    string = """Now we will prove foo.
<jh>
thm (foo () () (≠ 4 5) (
  proof here
))
</jh>
"""
    out = string_stream.OutputStream()
    ghilbert = convert.Wiki(string_stream.StringStream(string), "/general/file.gh", out).convert()
    self.assertEqual("Now we will prove foo.\n* #(≠ 4 5)# ([/general/file.gh/foo | foo])\n", out.contents())

  def test_add_multiple_references_to_theorems_to_wiki(self):
    string = """<jh>
thm (foo () () (≠ 4 5) (proof here))
thm (bar () () (≠ 4 6) (proof here))
thm (baz () () (≠ 4 7) (proof here))
</jh>
"""
    out = string_stream.OutputStream()
    ghilbert = convert.Wiki(string_stream.StringStream(string), "/general/file.gh", out).convert()
    self.assertEqual("""* #(≠ 4 5)# ([/general/file.gh/foo | foo])
* #(≠ 4 6)# ([/general/file.gh/bar | bar])
* #(≠ 4 7)# ([/general/file.gh/baz | baz])
""", out.contents())

  def test_show_hypotheses(self):
    string = """<jh>
thm (foo () ((H4 (< n 4)) (H2 (> n 2))) (= n 3) (
  proof here
))
</jh>
"""
    out = string_stream.OutputStream()
    ghilbert = convert.Wiki(string_stream.StringStream(string), "file.gh", out).convert()
    self.assertEqual("* #(< n 4)#, #(> n 2)# ⊢ #(= n 3)# ([file.gh/foo | foo])\n", out.contents())

  def test_import(self):
    converter = convert.Convert()
    opener = string_stream.Opener()
    converter.set_opener(opener)
    opener.set_file("Interface/P/r/i/Principia Mathematica propositional logic", string_stream.StringStream("""
thm (x y z) (do not try to parse me)
<jh>
kind (formula)
var (formula pp)
term (formula (¬ formula))
</jh>
"""))
    result = converter.convert(string_stream.StringStream("""
import (PRINCIPIA Interface:Principia_Mathematica_propositional_logic () ())
var (formula p)
thm (foo () ((H (p ¬))) (p ¬) (
        H
))
"""))
    self.assertEqual("""
import (PRINCIPIA Principia_Mathematica_propositional_logic.ghi () "")
tvar (formula p)
thm (foo () (H (¬ p)) (¬ p)
        H
 )
""", result)

  def test_export(self):
    converter = convert.Convert()
    opener = string_stream.Opener()
    converter.set_opener(opener)
    opener.set_file("Interface/P/r/o/Propositional logic",
      string_stream.StringStream(""))
    input = "export (INTUITIONISTIC Interface:Propositional_logic () ())"
    result = converter.convert(string_stream.StringStream(input))
    self.assertEqual('export (INTUITIONISTIC Propositional_logic.ghi () "")', result)

  def test_convert_filename_main(self):
    converter = convert.Convert()
    self.assertEqual("Main/R/e/l/Relations", converter.convert_filename(
      "Relations"))

  def test_convert_filename_interface(self):
    converter = convert.Convert()
    self.assertEqual("Interface/T/r/i/Trigonometry", converter.convert_filename(
      "Interface:Trigonometry"))

  def test_convert_filename_with_underscores(self):
    converter = convert.Convert()
    self.assertEqual("Interface/R/e/a/Real number axioms", converter.convert_filename(
      "Interface:Real_number_axioms"))

  def test_ghilbert_filename(self):
    converter = convert.Convert()
    self.assertEqual("Real_number_axioms.ghi", converter.ghilbert_filename(
      "Interface:Real_number_axioms"))

  def test_ghilbert_filename_main(self):
    converter = convert.Convert()
    self.assertEqual("Relations.gh", converter.ghilbert_filename(
      "Relations"))

  # Not a realistic test, in that kind is interface-only and thm
  # is proof-module-only. But we are a converter, not a verifier, so that is OK.
  def test_removes_parentheses_in_thm(self):
    result = self.process("""
kind (formula)
var (formula p)
term (formula (¬ formula))
thm (foo () ((H (p ¬))) (p ¬) (
  H
))
""")

    # The space before the last ')' is the one which was before the proof in jhilbert.
    # Perhaps nice to tidy that up, but for now don't worry about it.
    self.assertEqual("""
kind (formula)
tvar (formula p)
term (formula (¬ p))
thm (foo () (H (¬ p)) (¬ p)
  H
 )
""", result)

