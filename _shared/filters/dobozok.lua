--[[
dobozok.lua -- egységes, arculatos kiemelődobozok minden kimeneti formátumra.

Markdownban:
  ::: {.eset eset="B" title="VárosiBringa: kik az érdekeltek?"}
  szöveg ...
  :::

Típusok: cel, fogalom, eset, pelda, kitekintes, hiba, onell, projekt, prompt,
         osszefoglalo, forras.
Az önellenőrző dobozban egy {.megoldas} blokk HTML-ben lenyitható, PDF-ben
kisebb betűvel, a kérdések után jelenik meg.
]]

local alapcim = {
  cel = "Tanulási eredmények",
  fogalom = "Fogalom",
  eset = "Futó eset",
  pelda = "Kidolgozott példa",
  kitekintes = "Kitekintés",
  hiba = "Gyakori buktató",
  onell = "Önellenőrzés",
  projekt = "Projektlépés",
  prompt = "Mintaprompt",
  osszefoglalo = "Összefoglalás",
  forras = "Továbbolvasás",
}

local function latex_escape(s)
  s = s:gsub("\\", "\\textbackslash{}")
  s = s:gsub("([%%#&_%$])", "\\%1")
  s = s:gsub("~", "\\textasciitilde{}")
  return s
end

local function html_escape(s)
  return (s:gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"))
end

local function is_latex() return quarto.doc.is_format("latex") end
local function is_html() return quarto.doc.is_format("html") end
local function is_epub() return quarto.doc.is_format("epub") end

local function megoldas(el)
  if is_latex() then
    local b = { pandoc.RawBlock("latex", "\\begin{pemegoldas}") }
    for _, x in ipairs(el.content) do table.insert(b, x) end
    table.insert(b, pandoc.RawBlock("latex", "\\end{pemegoldas}"))
    return b
  elseif is_html() then
    local b = { pandoc.RawBlock("html", '<details class="megoldas"><summary>Megoldás</summary>') }
    for _, x in ipairs(el.content) do table.insert(b, x) end
    table.insert(b, pandoc.RawBlock("html", "</details>"))
    return b
  else
    local b = { pandoc.Para({ pandoc.Strong({ pandoc.Str("Megoldás") }) }) }
    for _, x in ipairs(el.content) do table.insert(b, x) end
    return { pandoc.Div(b, pandoc.Attr("", { "megoldas" })) }
  end
end

function Div(el)
  if el.classes:includes("megoldas") then
    return megoldas(el)
  end
  for tipus, cim in pairs(alapcim) do
    if el.classes:includes(tipus) then
      local title = el.attributes["title"] or cim
      local eset = el.attributes["eset"]
      local kulcs = tipus
      if tipus == "eset" and eset then kulcs = "eset" .. eset end
      -- belső megoldás-blokkok feldolgozása
      el = pandoc.walk_block(el, { Div = function(d)
        if d.classes:includes("megoldas") then return megoldas(d) end
      end })
      if is_latex() then
        local b = { pandoc.RawBlock("latex",
          "\\begin{pedoboz}{" .. kulcs .. "}{" .. latex_escape(title) .. "}") }
        for _, x in ipairs(el.content) do table.insert(b, x) end
        table.insert(b, pandoc.RawBlock("latex", "\\end{pedoboz}"))
        return b
      elseif is_html() or is_epub() then
        local fmt = is_html() and "html" or "html"
        local b = {
          pandoc.RawBlock(fmt, '<div class="doboz doboz-' .. kulcs .. '">' ..
            '<div class="doboz-cim">' .. html_escape(title) .. '</div><div class="doboz-tartalom">')
        }
        for _, x in ipairs(el.content) do table.insert(b, x) end
        table.insert(b, pandoc.RawBlock(fmt, "</div></div>"))
        return b
      else
        return el
      end
    end
  end
end
