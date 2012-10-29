# encoding: utf-8

import unittest
import tree
import tokenizer
import string_stream

class test_tree(unittest.TestCase):
  def process(self, inputString):
    return tree.parse(string_stream.StringStream(inputString))

  def read_expression(self, inputString):
    tokenizer1 = tokenizer.Tokenizer(string_stream.StringStream(inputString))
    return tree.read_expression(tokenizer1)

  def test_empty(self):
    tree = self.process("")
    self.assertEqual(0, tree.count())
    self.assertEqual([], tree.elements())

  def test_atom(self):
    tree = self.process("frog")
    self.assertEqual(1, tree.count())
    self.assertEqual(["frog"], tree.elements())

  def test_parenthesized_expression(self):
    tree = self.process("(5 gherkin flavour)")
    self.assertEqual(1, tree.count())
    self.assertEqual([["5", "gherkin", "flavour"]], tree.elements())

  def test_nested(self):
    tree = self.process("(= (+ (+ a b) c) (+ a (+ b c)))")
    self.assertEqual([["=", ["+", ["+", "a", "b"], "c"], ["+", "a", ["+", "b", "c"]]]],
      tree.elements())

  def test_multiple_top_level(self):
    tree = self.process("foo bar (5 6)")
    self.assertEqual(["foo", "bar", ["5", "6"]], tree.elements())

  def test_output_as_string(self):
    tree = self.process("foo bar (5 6)\n")
    self.assertEqual("foo bar (5 6)\n", tree.to_string())

  def test_single_atom_as_string(self):
    tree = self.process("foo")
    self.assertEqual("foo", tree.to_string())

  def test_single_list_as_string(self):
    tree = self.process("(foo)")
    self.assertEqual("(foo)", tree.to_string())

  def test_list_of_list_as_string(self):
    tree = self.process("((foo))")
    self.assertEqual("((foo))", tree.to_string())

  def test_no_particular_need_to_add_newline_to_end(self):
    tree = self.process("foo")
    self.assertEqual("foo", tree.to_string())

  def test_should_preserve_whitespace(self):
    self.assertEqual("  xyz  \t\n(formula\n)", self.process("  xyz  \t\n(formula\n)").to_string())

  def test_hash_to_end_of_line_is_comment(self):
    self.assertEqual(["foo"], self.process("  foo # a common metavariable").elements())

  def test_preserve_comments(self):
    self.assertEqual("  foo # bar", self.process("  foo # bar").to_string())

  def test_index_children(self):
    array = self.read_expression("(first second)")
    self.assertEqual("first", array[0])
    self.assertEqual("second", array[1])

  def test_read_two_expressions(self):
    inputString = "kind (formula)"
    tree = self.process(inputString)
    self.assertEqual("kind", tree[0])
    self.assertEqual("formula", tree[1].to_string())

  def test_can_change_item(self):
    tree = self.process("the quick brown fox")
    tree[2] = "red"
    self.assertEqual("the quick red fox", tree.to_string())

