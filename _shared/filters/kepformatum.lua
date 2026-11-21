--[[
kepformatum.lua -- vektoros ábrák formátumhoz illesztése.
A forrásban az ábrák SVG-ként szerepelnek (abrak/gen/*.svg).
PDF-kimenetnél a párhuzamosan generált, azonos nevű PDF-et használjuk,
így a nyomtatott változat is natív vektorgrafikát kap.
]]
function Image(el)
  if quarto.doc.is_format("latex") and el.src:match("%.svg$") then
    el.src = el.src:gsub("%.svg$", ".pdf")
  end
  return el
end
