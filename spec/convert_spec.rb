require 'rspec'
require './lib/convert'

describe "convert" do
  it "generates an empty file given an empty file" do
    input = StringIO.new("")
    Convert.new.process(input).should == ""
  end
end
