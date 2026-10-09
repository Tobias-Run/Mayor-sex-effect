-- Give Pandoc's LaTeX tables explicit wrapping widths on an A4 text block.
-- The same Markdown remains readable in GitHub without PDF-specific markup.
function Table(t)
  local first = pandoc.utils.stringify(t.head.rows[1].cells[1].contents)
  local widths
  if first == 'Margin at most (pp)' and #t.colspecs == 5 then
    widths = {0.18, 0.16, 0.22, 0.22, 0.22}
  elseif first == 'Margin at most (pp)' and #t.colspecs == 6 then
    widths = {0.14, 0.20, 0.08, 0.22, 0.18, 0.18}
  elseif first == 'Supported mixed-pair municipality' then
    widths = {0.29, 0.25, 0.27, 0.19}
  elseif first == 'Dimension' then
    widths = {0.26, 0.17, 0.20, 0.21, 0.16}
  elseif first == 'Scenario' then
    widths = {0.40, 0.12, 0.12, 0.18, 0.18}
  else
    error('Unreviewed PDF table layout: ' .. first)
  end
  assert(#widths == #t.colspecs, 'PDF table column count changed')
  for i, width in ipairs(widths) do
    t.colspecs[i][2] = width
  end
  -- Keep these short tables and their following caption together.
  return {pandoc.RawBlock('latex', '\\Needspace{18\\baselineskip}'), t}
end
