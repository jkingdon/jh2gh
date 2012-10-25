# encoding: utf-8

import unittest
import tokenizer
import string_stream

class test_tree(unittest.TestCase):
  def process(self, inputString):
    return tokenizer.tokenize(string_stream.StringStream(inputString))

  def test_empty(self):
    self.assertEqual(["\n"], self.process(""))

  def test_atom(self):
    self.assertEqual(["frog", "\n"], self.process("frog"))

  def test_parenthesized_expression(self):
    tokens = self.process("(5 gherkin flavour)")
    self.assertEqual(
      ["(", "5", " ", "gherkin", " ", "flavour", ")", "\n"],
      tokens)

  def test_nested(self):
    tokens = self.process("((x)y()())")
    self.assertEqual(["(", "(", "x", ")", "y", "(", ")", "(", ")", ")", "\n"],
      tokens)

  def test_whitespace_tokens(self):
    self.assertEqual(["  ", "xyz", "  \t\n", "(", "formula", "\n", ")", "\n"],
      self.process("  xyz  \t\n(formula\n)"))

  def test_comment_token(self):
    self.assertEqual(["  ", "foo", " ", "# a common metavariable\n"],
      self.process("  foo # a common metavariable"))

  def test_line_following_comment_is_not_a_comment(self):
    self.assertEqual(["# comment\n", "a", " ", "b", "\n"],
      self.process("# comment\na b"))

