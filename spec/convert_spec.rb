# encoding: utf-8

require 'rspec'
require './lib/convert'

describe "convert" do
  def process(input)
    Convert.new.process(StringIO.new(input))
  end

  it "generates an empty file given an empty file" do
    process("").should == ""
  end

  it "can convert kind to kind" do
    process("kind (formula)").should == "kind (formula)"
  end

  it "converts var to tvar by default" do
    process("kind (formula)\nvar (formula p)").should == "kind (formula)\ntvar (formula p)"
  end

  it "converts var to var for kind variable" do
    process("kind (object)\nkind (variable)\nvar (variable x)").should ==
      "kind (object)\nvar (object x)"
  end

  it "can convert a basic stmt" do
    pending "not too close to getting this one working yet"
    gh = process <<END
kind (formula)
var (formula p q)
term (formula (→ formula formula))
stmt (AntecedentIntroduction () () (p → (q → p)))
END
      gh.should == <<END
kind (formula)
tvar (formula p q)
term (formula (→ p q))
stmt (AntecedentIntroduction () () (→ p (→ q p)))
END
  end
end
