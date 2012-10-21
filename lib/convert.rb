class Convert
  def process(input_stream)
    input = input_stream.read
    input.
      gsub(/^kind \(variable\)\n/, "").
      gsub(/^var \(([^v])/, 'tvar (\1').
      gsub(/^var \(variable/, "var (object")
  end
end

