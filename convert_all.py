import os
import sys
import convert

class ConvertAll:
  def convert(self, underscored_name):
    sys.stdout.write('Converting ' + underscored_name + "\n")
    convert.FileConverter().convert(underscored_name)

  def run(self):
    os.chdir('../wikiproofs')

    self.convert('Interface:Axioms_of_intuitionistic_propositional_logic')
    self.convert('Intuitionistic_propositional_logic')
    self.convert('Interface:Basic_intuitionistic_propositional_logic')
    self.convert('Interface:Law_of_the_excluded_middle')
    self.convert('From_intuitionistic_to_classical_propositional_logic')
    self.convert('Interface:Principia_Mathematica_propositional_logic_theorems')
    self.convert('Convenience_theorems_of_propositional_logic')
    self.convert('Interface:Classical_propositional_calculus')

#    self.convert('Interface:Axioms_of_first-order_logic')


if __name__ == '__main__':
#  sys.stderr.write('Usage: python convert_all.py\n')
  sys.stdout.write('Converting selected files from ../wikiproofs\n')
  sys.stdout.write('And putting the output in ../ghilbert-app/general\n')
  ConvertAll().run()

