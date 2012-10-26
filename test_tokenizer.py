# encoding: utf-8

import unittest
import tokenizer
import string_stream

class test_tree(unittest.TestCase):
  def process(self, inputString):
    return tokenizer.tokenize(string_stream.StringStream(inputString))

  def test_empty(self):
    self.assertEqual([], self.process(""))

  def test_atom(self):
    self.assertEqual(["frog"], self.process("frog"))

  def test_does_not_double_final_newline(self):
    self.assertEqual(["frog", "\n"], self.process("frog\n"))

  def test_parenthesized_expression(self):
    tokens = self.process("(5 gherkin flavour)")
    self.assertEqual(
      ["(", "5", " ", "gherkin", " ", "flavour", ")"],
      tokens)

  def test_nested(self):
    tokens = self.process("((x)y()())")
    self.assertEqual(["(", "(", "x", ")", "y", "(", ")", "(", ")", ")"],
      tokens)

  def test_whitespace_tokens(self):
    self.assertEqual(["  ", "xyz", "  \t\n", "(", "formula", "\n", ")"],
      self.process("  xyz  \t\n(formula\n)"))

  def test_comment_token_ending_file_without_newline(self):
    self.assertEqual(["  ", "foo", " ", "# a common metavariable"],
      self.process("  foo # a common metavariable"))

  def test_line_following_comment_is_not_a_comment(self):
    self.assertEqual(["# comment\n", "a", " ", "b"],
      self.process("# comment\na b"))

  def test_next_token(self):
    inputString = "token1 "
    stream = string_stream.StringStream(inputString)
    tokenizer1 = tokenizer.Tokenizer(stream)
    self.assertEqual("token1", tokenizer1.next_token())
    self.assertEqual(" ", tokenizer1.next_token())
    self.assertEqual(None, tokenizer1.next_token())

