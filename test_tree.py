# encoding: utf-8

import unittest
import tree
import string_stream

class test_tree(unittest.TestCase):
  def process(self, inputString):
    return tree.parse(string_stream.StringStream(inputString))

  def test_empty(self):
    tree = self.process("")
    self.assertEqual(0, tree.count())

  def test_atom(self):
    tree = self.process("frog")
    self.assertEqual(1, tree.count())
    self.assertEqual("frog", tree.text())

