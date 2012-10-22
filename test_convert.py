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

  def xtest_should_preserve_whitespace(self):
    self.assertEqual("kind  \t\n(formula)", self.process("kind  \t\n(formula)"))

  def test_var_to_tvar(self):
    self.assertEqual("kind (formula)\ntvar (formula p)", self.process(
      "kind (formula)\nvar (formula p)"))

  def test_converts_var_to_var_for_kind_variable(self):
    self.assertEqual("kind (object)\nvar (object x)", self.process(
      "kind (object)\nkind (variable)\nvar (variable x)"))

#  it "can convert a basic stmt" do
#    pending "not too close to getting this one working yet"
#    gh = process <<END
#kind (formula)
#var (formula p q)
#term (formula (→ formula formula))
#stmt (AntecedentIntroduction () () (p → (q → p)))
#END
#      gh.should == <<END
#kind (formula)
#tvar (formula p q)
#term (formula (→ p q))
#stmt (AntecedentIntroduction () () (→ p (→ q p)))
#END
#  end
#end
