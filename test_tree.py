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
    self.assertEqual(0, len(tree))
    self.assertEqual([], tree.elements_children_as_trees())

  def test_atom(self):
    tree = self.process("frog")
    self.assertEqual(1, len(tree))
    self.assertEqual(["frog"], tree.elements_children_as_trees())

  def test_parenthesized_expression(self):
    tree = self.process("(5 gherkin flavour)")
    self.assertEqual(1, len(tree))
    self.assertEqual(["5", "gherkin", "flavour"],
      tree[0].elements_children_as_trees())

  def test_nested(self):
    tree = self.process("(- (+ a b))")
    elements = tree.elements_children_as_trees()[0]
    self.assertEqual("-", elements[0])
    self.assertEqual(["+", "a", "b"], elements[1].elements_children_as_trees())

  def test_deeply_nested(self):
    tree = self.process("(= (+ (+ a b) c) (+ a (+ b c)))")
    self.assertEqual("(= (+ (+ a b) c) (+ a (+ b c)))", repr(tree))

  def test_multiple_top_level(self):
    tree = self.process("foo bar (5 6)")
    self.assertEqual("foo", tree[0])
    self.assertEqual("bar", tree[1])
    self.assertEqual("5 6", repr(tree[2]))

  def test_output_as_string(self):
    tree = self.process("foo bar (5 6)\n")
    self.assertEqual("foo bar (5 6)\n", repr(tree))

  def test_single_atom_as_string(self):
    tree = self.process("foo")
    self.assertEqual("foo", repr(tree))

  def test_single_list_as_string(self):
    tree = self.process("(foo)")
    self.assertEqual("(foo)", repr(tree))

  def test_list_of_list_as_string(self):
    tree = self.process("((foo))")
    self.assertEqual("((foo))", repr(tree))

  def test_no_particular_need_to_add_newline_to_end(self):
    tree = self.process("foo")
    self.assertEqual("foo", repr(tree))

  def test_should_preserve_whitespace(self):
    self.assertEqual("  xyz  \t\n(formula\n)", repr(self.process("  xyz  \t\n(formula\n)")))

  def test_hash_to_end_of_line_is_comment(self):
    tree = self.process("  foo # a common metavariable")
    self.assertEqual(["foo"], tree.elements_children_as_trees())

  def test_preserve_comments(self):
    self.assertEqual("  foo # bar", repr(self.process("  foo # bar")))

  def test_all_elements(self):
    self.assertEqual(["  ", "foo", " ", "# bar"],
      self.process("  foo # bar").all_elements())

  def test_cannot_modify_via_all_elements(self):
    tree = self.process("foo")
    elements = tree.all_elements()
    elements[0] = "bar"
    self.assertEqual("foo", repr(tree))

  def test_as_string_skips_wiki(self):
    input_string = """This is a file.
<jh>
kind (formula)
</jh>
And it ends."""
    tokenizer1 = tokenizer.Tokenizer(tokenizer.WikiTokenizer(string_stream.StringStream(input_string)))
    t = tree.parse_from_tokenizer(tokenizer1)
    self.assertEqual("kind (formula)\n", repr(t))

  def tree_from_wiki(self, input_string):
    tokenizer1 = tokenizer.Tokenizer(tokenizer.WikiTokenizer(string_stream.StringStream(input_string)))
    return tree.parse_from_tokenizer(tokenizer1)

  def test_to_string_wiki_to_comment(self):
    input_string = """This is a file.
<jh>
kind (formula)
</jh>
And it ends."""
    t = self.tree_from_wiki(input_string)
    self.assertEqual("""# This is a file.
kind (formula)
# And it ends.""", t.to_string_wiki_to_comment())

  def test_to_string_wiki_to_comment_nested(self):
    input_string = """<jh>
(
</jh>
Here is a comment.
<jh>
)
"""
    t = self.tree_from_wiki(input_string)
    self.assertEqual("""(
# Here is a comment.
)
""", t.to_string_wiki_to_comment())

  def test_to_string_wiki_to_wiki_out(self):
    input_string = """This is a file.
<jh>
kind (formula)
</jh>
And it ends."""
    t = self.tree_from_wiki(input_string)
    wiki_out = string_stream.OutputStream()
    proof = t.to_string_wiki_to_wiki_out(wiki_out)
    self.assertEqual("kind (formula)\n", proof)
    self.assertEqual("This is a file.\nAnd it ends.", wiki_out.contents())

  def test_wiki_text_in_proofs_ends_up_as_comments(self):
    input_string = """<jh>
thm (x () () result
</jh>
We will start with a proof.
<jh>
    proof steps
)
</jh>
"""
    t = self.tree_from_wiki(input_string)
    wiki_out = string_stream.OutputStream()
    proof = t.to_string_wiki_to_wiki_out(wiki_out)
    self.assertEqual("""thm (x () () result
# We will start with a proof.
    proof steps
)
""", proof)
    self.assertEqual("", wiki_out.contents())

  def test_all_elements_includes_wiki_nodes(self):
    subtree = tree.Tree("formula")
    wiki_node = tokenizer.Wiki("We define a kind called formula")
    sample_tree = tree.Tree([wiki_node, "kind", subtree])
    self.assertEqual([wiki_node, "kind", subtree], sample_tree.all_elements())

  def test_elements_children_as_trees_does_not_include_wiki_nodes(self):
    subtree = tree.Tree("formula")
    sample_tree = tree.Tree([tokenizer.Wiki("We define a kind called formula"), "kind", subtree])
    self.assertEqual(["kind", subtree], sample_tree.elements_children_as_trees())

  def test_index_children(self):
    array = self.read_expression("(first second)")
    self.assertEqual("first", array[0])
    self.assertEqual("second", array[1])

  def test_read_two_expressions(self):
    inputString = "kind (formula)"
    tree = self.process(inputString)
    self.assertEqual("kind", tree[0])
    self.assertEqual("formula", repr(tree[1]))

  def test_can_change_item(self):
    tree = self.process("the quick brown fox")
    tree[2] = "red"
    self.assertEqual("the quick red fox", repr(tree))

  def test_setting_item_works_with_wiki(self):
    sample_tree = tree.Tree([tokenizer.Wiki("We define a kind\n"), "kynd"])
    sample_tree[0] = "kind"
    self.assertEqual("# We define a kind\nkind", sample_tree.to_string_wiki_to_comment())

  def test_insert(self):
    tree = self.process("")
    tree.insert(0, ["foo"])
    self.assertEqual("foo", repr(tree))

  def test_insert_indexes_do_not_count_whitespace(self):
    tree = self.process(" foo")
    tree.insert(1, ["bar"])
    self.assertEqual(" foobar", repr(tree))

  def test_insert_but_not_at_end(self):
    tree = self.process(" bar")
    tree.insert(0, ["foo"])
    self.assertEqual("foo bar", repr(tree))

  def test_insert_multiple(self):
    tree = self.process("foo")
    tree.insert(1, ["-", "bar", "\n", "# I'm inserting!"])
    self.assertEqual("foo-bar\n# I'm inserting!", repr(tree))

