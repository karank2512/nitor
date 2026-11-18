# Round 4 (PRIVATE PROOF) - separate Clean / Trace statics

Sources: `glyphs.py` (geometry, original), `build.py`, `render.py`. Old run-2 sources and proofs
stay untouched in `../stage0/`. Diagnosis tools are in `../diag/`.

## Changes vs run 2 (r3)
Clean (letters only):
- squarer rounds on o 0 a g n (superelliptic handles 0.68-0.74)
- signature 45-degree chamfer (26u) on free stroke ends: i/1 slabs + spurs, 1 flag tip, l spur + foot, brace arm tips
- braces rebuilt from straight segments: 45-degree corners and a 45-degree pinch with a short flat nose
- n arch springs higher and narrower from the stem
Trace (separate static display style, construction per glyph):
- no full-width rules at all; stem-edge overshoot lines, compass-centre crosses, top/bottom extreme
  ticks, the n arch's own oval, open arcs continuing s and g past their terminals, the 1 flag
  diagonal extended, and brace corner marks + an X where the pinch diagonals cross
- r4b: s rings -> open arcs (full rings closed s into '8'); l foot tick read as '=' -> one line; i dot marks removed
- r4c: o/a/g/0 side ticks removed (they chained into a dashed strike line at mid-height)

## Still weak
- s and g are the least distinctive glyphs; the chamfer only appears where a free end is straight
- Trace at 13px is not for text: the construction thickens letters into a blotchy texture
- brace pinch construction partly overlaps the ink edges (reads slightly heavier)
- overlapping contours (no overlap removal without skia-pathops), unhinted, wght 400 only
