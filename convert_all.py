import os
import sys
import convert

class ConvertAll:
  def convert(self, underscored_name):
    sys.stdout.write('Converting ' + underscored_name + "\n")
    convert.FileConverter().convert(underscored_name)

  def run(self):
    os.chdir('../wikiproofs')
    self.convert('Intuitionistic_propositional_logic')

if __name__ == '__main__':
#  sys.stderr.write('Usage: python convert_all.py\n')
  sys.stdout.write('Converting selected files from ../wikiproofs\n')
  sys.stdout.write('And putting the output in ../ghilbert-app/general\n')
  ConvertAll().run()

