# Stage 0 notes (PRIVATE PROOF, provisional internal name only)

Glyphs: H n o a g s 0 { } i l 1 (+ space, .notdef), wght 400 only.
Sources: `glyphs.py` (all geometry, original), `build.py`, `render.py`, `measure_trce0.py`.
Tools: existing fontTools 4.39.4 + Pillow 9.5.0 in the python.org 3.11 framework (run as-is, nothing
installed), Google Chrome 157 headless (profile in `../.chrome-proof-profile`, git-ignored),
hb-view 11.0.0 for a FreeType cross-check.

## Rounds
- r1: first geometry. Clean read well at 13px. Ghost r1 (cell edges + stem centrelines + guides) read as a cage.
  Found: zero-width ghost visible at TRCE 0 in Chrome/macOS default smoothing.
- r2: g tail and 1 flag changed from angled to flat vertical cuts (brief rule 8); l foot bottom raised -10 -> -4;
  ghost cut down to metric rules + real construction (n arch circle, s stacked circles, g tail circle,
  o/0/a tangent guides, 1 flag guide, brace axis).
- r3: l foot circle ghost read as a 'b' bowl -> replaced with a stem guide.

## TRCE 0 measurement (13px, Chrome, identical layout, diff vs Clean static)
- control (Clean ink + fvar + empty gvar, no ghost): 0 pixels changed (both smoothing modes)
- default macOS smoothing: z0 3948 px >15 levels, h2 4290 -> ghost lines visible as rules
- -webkit-font-smoothing: antialiased: z0 1678, h2 1779 -> no visible lines, but glyph edges change
- FreeType/cairo (hb-view): z0 vs Clean = 0 pixels changed
Verdict: ghost-in-every-master is not safe for text on macOS -> separate Clean (no ghost contours)
and Trace display styles; any fade is compositing.

## Deviations from the brief (proposals, not decisions)
- 0 has a centered square dot (the brief said slash-free); it follows the square-dot motif and
  separates 0 from O in code.
- The ghost drops cell edges and stem centrelines (they read as a cage).
